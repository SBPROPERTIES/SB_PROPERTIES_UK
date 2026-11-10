const fs = require('fs');
const glob = require('glob');

const blogFiles = fs.readdirSync('blog').filter(f => f.endsWith('.html') && f !== 'index.html');

blogFiles.forEach(file => {
    let content = fs.readFileSync(`blog/${file}`, 'utf8');

    // Fix relative paths for images in the blog/ directory to point up to root
    content = content.replace(/src="logo.webp"/g, 'src="../logo.webp"');
    
    // Fix navigation link hrefs
    content = content.replace(/href="blog\/index\.html"/g, 'href="index.html"'); // Blog to Blog Hub Link
    content = content.replace(/href="index\.html"/g, 'href="../index.html"'); // The above will get re-replaced, so we need to be careful.
    
    // Actually, let's just use string replace carefully
    
});
