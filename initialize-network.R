# INITIALIZE NETWORK --------------
# (add preliminary network structure to population)

rm(list=ls())


# Load libraries ---------------------------

library(ergm)
library(tergm)
library(networkDynamic)

seed <- runif(n = 1, min = 1, max = 1e4)
set.seed(seed = seed)

# Load Data  ---------------------------

load(file="init-population.RData")


# Define needed parameters  ---------------------------

formation <- ~edges
mean_deg <- 3
nedges <- n*mean_deg/2
target.stats <- c(nedges)
constraints <- ~.
duration <- 2500 
theta.diss <- log(duration-1)
dissolution <- ~offset(edges)

formation.n0 <- update.formula(formation, n0~.)

n0 <- network.initialize(n, directed=FALSE, bipartite=FALSE)

fit1 <- ergm(formation.n0, 
            target.stats=target.stats, 
            constraints=constraints,
            eval.loglik=FALSE,
            verbose=TRUE,
            control=control.ergm(MCMLE.maxit=500)
            )
summary(fi1t)
theta.form.1 <- fit1$coef 

sim1 <- simulate(fit1,nsim=1,
                 control=control.simulate.ergm(MCMC.burnin=1000))
plot(sim1)

theta.form.2 <- theta.form.1
theta.form.2[1] <- theta.form.2[1] - theta.diss

sim2 <- simulate(n0,
                 formation=formation.n0,
                 dissolution=~edges,
                 coef.form=theta.form.2,
                 coef.diss=theta.diss,
                 #time.slices=2e4,
                 time.slices=5e4,
                 constraints=constraints,
                 monitor="all"
)
summary(sim2)
network.collapse(sim2, at=1)
network.collapse(sim2, at=100)
network.collapse(sim2, at=5e4-1)
network.collapse(sim2, at=5e4)
network.collapse(sim2, at=5e4+100)

save.image(file="intialized-network.RData")