library(yaml)
library(ncdf4)
library(ggplot2)
# library(gridExtra)

################################################################################
#Load ESMValTool stuff
args <- commandArgs(trailingOnly = TRUE)
params <- read_yaml(args[1])

# define the directories
plot_dir <- params$plot_dir
run_dir <- params$run_dir
work_dir <- params$work_dir
dir.create(run_dir, recursive = TRUE)
dir.create(plot_dir, recursive = TRUE)
dir.create(work_dir, recursive = TRUE)

for (i in 1:length(params$input_files)){
  metadata1 <- read_yaml(params$input_files[i])
  combined_plot <- ggplot()
  for(j in 1:length(metadata1)){
    nc <- nc_open(metadata1[[j]]$filename)
    gcm <- metadata1[[j]]$dataset
    var_group <- metadata1[[j]]$variable_group
    print(paste("NetCDF of dataset", gcm, "in variable group", var_group, ":"))
    print(nc)
    dim_names <- names(nc$dim)
    if (("lat" %in% dim_names) && ("lon" %in% dim_names)){
      lat <- ncvar_get(nc,"lat")
      lon <- ncvar_get(nc,"lon")
      tas <- ncvar_get(nc, "tas")
      df <- expand.grid(lon = lon, lat = lat)
      df$tas <- as.vector(tas)
      combined_plot <- ggplot(df, aes(x = lon, y = lat, fill = tas)) +
                      geom_raster() +
                      scale_fill_gradient(low = "red", high = "yellow", na.value = "transparent")
      labs <- labs(fill = "Temperature (°C)")
    }
    else if ("time" %in% dim_names){
      df <- data.frame(time=ncvar_get(nc,"time"), value = ncvar_get(nc, "tas"))
      combined_plot <- combined_plot + geom_line(data=df, aes(x = time, y = value))
      labs <- labs(x="time",y="air_temperature/degC",title=metadata1[[j]]$caption)
    }
  }
  combined_plot <- combined_plot  + labs
  ggsave(paste0(plot_dir,"/var",i,metadata1[[j]]$savefig), plot = combined_plot, width = 8, height = 6, units = "in")
}
