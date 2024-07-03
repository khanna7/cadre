library(data.table)
library(jsonlite)

dta <- data.table(BASE_SEED = 1:30)

fileConn <- file("experiment_seeds.txt")
jsonlite::stream_out(dta, con=fileConn)
#close(fileConn)