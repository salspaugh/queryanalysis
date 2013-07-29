
data <- read.csv("/data/deploy/boss/data.storm/svd/sparse_arg_usage_matrix_tfidf.csv")
m <- sparseMatrix(i = data$row, j = data$col, x = data$cnt, index1 = FALSE)

#m <- log(m)
#m[m == 0] <- .5
#m[m == -Inf] <- 0
#m <- 1/sqrt(m)
#m[m == Inf] <- 2

m.svd <- irlba(m, nu=2, nv=2)
u.x.scaled <- m.svd$u[,1]*m.svd$d[1]
u.y.scaled <- m.svd$u[,2]*m.svd$d[2]
v.x.scaled <- m.svd$v[,1]*m.svd$d[1]
v.y.scaled <- m.svd$v[,2]*m.svd$d[2]
u.scaled <- cbind(u.x.scaled, u.y.scaled)
v.scaled <- cbind(v.x.scaled, v.y.scaled)

write.csv(u.scaled, "/data/deploy/boss/data.storm/svd/tfidf_args2d.csv")
write.csv(v.scaled, "/data/deploy/boss/data.storm/svd/tfidf_usages2d.csv")
