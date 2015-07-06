Code for extracting text from Wikipedia
=======================================
For each language X (e.g., X="en", X="ko", etc.):

* Download the latest XML file from the following URL:

http://download.wikimedia.org/Xwiki/latest/Xwiki-latest-pages-articles.xml.bz2

For example, for English we use

http://download.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

* Use the Python script by Giuseppe Attardi to extract the text portion. I've
modified a couple of lines so that it doesn't write doc info ("<doc id=...>" and
"</doc>") in the header and the footer. Use it on an (uncompressed) XML file
[xml] to obtain a single text file [txt] like this:

`python WikiExtractor.py [xml] -cb 250K -o temp_dir`
`find temp_dir -name '*bz2' -exec bunzip2 -c {} \; > [txt]`
`rm -rf temp_dir`