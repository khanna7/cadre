

# Intersections in multiple vectors ---------------------------
  # REF https://stackoverflow.com/questions/3695677/how-to-find-common-elements-from-multiple-vectors
intersect_all <- function(a,b,...){
  Reduce(intersect, list(a,b,...))
}

