script_dir <- getSrcDirectory(function(dummy) { })
print(script_dir)
print("111111111111111111")

args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])
script_dir <- dirname(script_path)

print(script_dir)

print("333333333333333333")

library(rprojroot)

# Get the directory of the running script
script_dir <- find_rstudio_root_file()
print(script_dir)