library(ggplot2)
library(MASS)
library(ggthemes)
library(LSD)

argv<-commandArgs(trailingOnly = TRUE)
data<-read.table(argv[1], header=T)
fig<-argv[2]



p = ggplot(data, aes(x=window, y=cov))

p + geom_point() + geom_line() + facet_wrap(. ~ chrom, scales = "free", ncol=1)	+ scale_y_continuous(trans='log10', labels = scales::comma) + scale_x_continuous(labels = scales::comma)

ggsave(fig, plot=last_plot(), dpi=300, width=7, height=50, limitsize=FALSE)
