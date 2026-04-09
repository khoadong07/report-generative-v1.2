#!/usr/bin/env node
/**
 * Script merge slide1_merged.html và slide2_merged.html thành 1 file HTML và convert sang PDF
 * Requires: puppeteer, cheerio
 * Install: npm install puppeteer cheerio
 */

const fs = require('fs').promises;
const path = require('path');
const cheerio = require('cheerio');
const puppeteer = require('puppeteer');

/**
 * Merge tất cả 16 slides thành 1 file HTML
 */
async function mergeHtmlFiles() {
    const outputDir = path.join(__dirname, 'output');
    const mergedFile = path.join(outputDir, 'merged_slides.html');
    
    // Collect all slide files (slide1_merged.html to slide16_merged.html)
    const slideFiles = [];
    for (let i = 1; i <= 16; i++) {
        const slideFile = path.join(outputDir, `slide${i}_merged.html`);
        try {
            await fs.access(slideFile);
            slideFiles.push(slideFile);
        } catch {
            console.log(`⚠️  File không tồn tại: slide${i}_merged.html (bỏ qua)`);
        }
    }

    if (slideFiles.length === 0) {
        console.log('❌ Không tìm thấy file slide nào!');
        return null;
    }

    console.log(`📄 Đang merge ${slideFiles.length} slides...`);

    // HTML template
    const htmlTemplate = `<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Merged Report - 16 Slides</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.1.0"></script>
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', sans-serif;
        background-color: #e5e7eb;
        padding: 0;
    }
    
    .slide-container {
        position: relative;
        width: 1280px;
        height: 720px;
        background-color: #f5f7fa;
        overflow: hidden;
        margin: 20px auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        page-break-after: always;
    }
    
    @media print {
        body {
            background-color: #ffffff;
            padding: 0;
        }
        
        .slide-container {
            margin: 0;
            box-shadow: none;
            page-break-after: always;
        }
    }
    
    /* Additional styles from individual slides */
</style>
</head>
<body>
`;

    const htmlContent = [htmlTemplate];
    const scripts = [];
    const styles = []; // Collect all style tags

    // Process all slides
    for (let idx = 0; idx < slideFiles.length; idx++) {
        const slideFile = slideFiles[idx];
        const content = await fs.readFile(slideFile, 'utf-8');
        
        // Extract styles using regex BEFORE parsing with cheerio
        const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
        let styleMatch;
        while ((styleMatch = styleRegex.exec(content)) !== null) {
            const styleContent = styleMatch[1];
            if (styleContent && styleContent.trim().length > 0) {
                // Extract only table-related styles, not body/slide-container
                const lines = styleContent.split('\n');
                const tableStyles = [];
                let inTableBlock = false;
                let currentBlock = [];
                
                for (const line of lines) {
                    const trimmed = line.trim();
                    
                    // Start of a CSS block
                    if (trimmed.includes('{')) {
                        const selector = trimmed.split('{')[0].trim();
                        if (selector.startsWith('table') || 
                            selector.startsWith('th') || 
                            selector.startsWith('td') || 
                            selector.startsWith('tr') ||
                            selector.includes('.nsr-')) {
                            inTableBlock = true;
                            currentBlock = [line];
                        }
                    } else if (inTableBlock) {
                        currentBlock.push(line);
                        if (trimmed.includes('}')) {
                            tableStyles.push(currentBlock.join('\n'));
                            inTableBlock = false;
                            currentBlock = [];
                        }
                    }
                }
                
                if (tableStyles.length > 0) {
                    console.log(`📝 Extracted ${tableStyles.length} table style blocks from slide ${idx + 1}`);
                    styles.push(tableStyles.join('\n'));
                }
            }
        }
        
        // Parse HTML
        const $ = cheerio.load(content);
        
        // Extract slide container
        const slideContainer = $('.slide-container');
        
        if (slideContainer.length > 0) {
            // Add slide ID
            slideContainer.attr('id', `slide-${idx + 1}`);
            
            // Extract scripts BEFORE removing them
            $('script').each((i, elem) => {
                const scriptContent = $(elem).html();
                if (scriptContent && (scriptContent.includes('chart') || scriptContent.includes('ctx') || scriptContent.includes('Chart'))) {
                    let modifiedScript = scriptContent;
                    
                    // Update canvas IDs in JavaScript for all slides except first
                    if (idx > 0) {
                        // Find all getElementById calls and add suffix
                        const slideNum = idx + 1;
                        modifiedScript = modifiedScript.replace(/getElementById\(['"](\w+)['"]\)/g, function(match, id) {
                            return `getElementById('${id}_${slideNum}')`;
                        });
                    }
                    
                    scripts.push(modifiedScript);
                }
            });
            
            // Update canvas IDs to avoid conflicts (add suffix for all slides except first)
            if (idx > 0) {
                // Update ALL element IDs in the slide container (not just canvas)
                slideContainer.find('[id]').each((i, elem) => {
                    const oldId = $(elem).attr('id');
                    if (oldId) {
                        const newId = oldId + '_' + (idx + 1);
                        $(elem).attr('id', newId);
                    }
                });
            }
            
            // Remove script tags from slide container (we'll add them separately)
            slideContainer.find('script').remove();
            
            htmlContent.push($.html(slideContainer));
        } else {
            console.log(`⚠️  Không tìm thấy slide-container trong ${path.basename(slideFile)}`);
        }
    }

    // Add all additional styles
    if (styles.length > 0) {
        console.log(`✅ Adding ${styles.length} style blocks to merged HTML`);
        htmlContent.push('<style>');
        htmlContent.push(styles.join('\n'));
        htmlContent.push('</style>');
    } else {
        console.log('⚠️  No additional styles found');
    }
    
    // Add all scripts wrapped in IIFE to avoid variable conflicts
    scripts.forEach((script, idx) => {
        htmlContent.push(`<script>(function() { ${script} })();</script>`);
    });

    // Close HTML
    htmlContent.push('</body>\n</html>');

    // Write merged file
    await fs.writeFile(mergedFile, htmlContent.join('\n'), 'utf-8');

    const stats = await fs.stat(mergedFile);
    console.log(`✅ Đã merge thành công: ${mergedFile}`);
    console.log(`📊 Kích thước file: ${(stats.size / 1024).toFixed(2)} KB`);
    
    return mergedFile;
}

/**
 * Export HTML file sang PDF sử dụng Puppeteer
 */
async function exportToPdf(htmlFile) {
    const pdfFile = htmlFile.replace('.html', '.pdf');

    console.log(`\n📄 Đang load HTML: ${htmlFile}`);
    console.log(`📦 Đang export sang: ${pdfFile}`);

    const browser = await puppeteer.launch({
        headless: 'new'
    });

    const page = await browser.newPage();

    // Set viewport
    await page.setViewport({
        width: 1280,
        height: 720
    });

    // Load HTML file
    await page.goto(`file://${htmlFile}`, {
        waitUntil: 'networkidle0'
    });

    // Wait for slides to load
    console.log('⏳ Đang đợi slides load...');
    await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds for dynamic content

    // Export to PDF
    console.log('📄 Đang tạo PDF...');
    await page.pdf({
        path: pdfFile,
        width: '1280px',
        height: '720px',
        printBackground: true,
        margin: {
            top: '0',
            right: '0',
            bottom: '0',
            left: '0'
        }
    });

    await browser.close();

    const stats = await fs.stat(pdfFile);
    console.log(`✅ Đã export PDF thành công: ${pdfFile}`);
    console.log(`📊 Kích thước file: ${(stats.size / 1024).toFixed(2)} KB`);
    
    return true;
}

/**
 * Main function
 */
async function main() {
    console.log('='.repeat(60));
    console.log('🚀 MERGE & CONVERT HTML TO PDF');
    console.log('='.repeat(60));

    try {
        // Step 1: Merge HTML files
        const mergedFile = await mergeHtmlFiles();

        if (!mergedFile) {
            console.log('\n❌ Merge thất bại!');
            process.exit(1);
        }

        // Step 2: Export to PDF
        console.log('\n' + '='.repeat(60));
        console.log('📄 CONVERTING TO PDF');
        console.log('='.repeat(60));

        const success = await exportToPdf(mergedFile);

        if (success) {
            console.log('\n' + '='.repeat(60));
            console.log('✅ HOÀN THÀNH!');
            console.log('='.repeat(60));
            console.log(`📁 HTML: ${mergedFile}`);
            console.log(`📁 PDF: ${mergedFile.replace('.html', '.pdf')}`);
        } else {
            console.log('\n❌ Export PDF thất bại!');
            process.exit(1);
        }
    } catch (error) {
        console.error('\n❌ Lỗi:', error.message);
        process.exit(1);
    }
}

// Run main function
if (require.main === module) {
    main();
}

module.exports = { mergeHtmlFiles, exportToPdf };
