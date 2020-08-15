# RP (Retinitis Pigmentosa) Gene Mapping
Work is supplemental to the paper "Applying Gene Discovery and Gene Mapping to Identifying the Underlying Causes of Retinitis Pigmentosa", by Yu chien (Calvin) Ma, Akaash Venkat, Chun-Yu (Audi) Liu, Su Bin Yoon, and Dr. Jie Zheng.

- - - -

Note: The files here were run on Python 2.7.16.

- - - -

Note that it's not necessary to setup and run the code from scratch as the SVG files included in the paper are found in the svg_files folder.


To setup and run the code:

* Download the code from the repository
* Using either Terminal (on Mac or Linux) or Powershell (on Windows), get into the RP-Gene-Mapping folder that was downloaded
* Using Terminal or Powershell, run "python download_gene_map.py"
    * Due to the heavy load of automation in this program, there is a chance running this program will crash. If this happens, just re-run "python download_gene_map.py" and the program will pick up from where it left off.
* Once "download_gene_map.py" is done running, there will be a file called "string_vector_graphic.svg" that will be saved to your computer's Downloads folder. Relocate that SVG file into the svg_files folder, and rename the file as "original_gene_map.svg"
* Using Terminal or Powershell, run "python restructure_gene_map.py"
* Using Terminal or Powershell, run "python recolor_gene_map.py"
* Using Terminal or Powershell, run "python find_connection_counts.py"

The final SVG files can be found in the svg_files folder.
