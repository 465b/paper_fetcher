# paper fetcher

A small script that downloads lists of papers from SciHub.
Designed to work in conjunction with SysRev's export function.

Takes ```csv``` or ```xml```(Evernote Format) files as input.
Looks up the title and author on CrossRef to fetch the doi.
Takes the doi to download the paper from SciHub.