# Redraw only the frozen Review 1 restart predictions for the new submission.
# The original Review 1 report and its historical figure remain unchanged.
pred <- read.csv('output/review1/policy_predictions.csv')
png('output/review1_presentation/restart_predictions.png', width=1500, height=580, res=160)
par(mar=c(4.3,4.7,2.5,1), mgp=c(2.8,.8,0), family='sans', cex=1.05)
cols <- c('#175F96','#667784','#A3ABB0')
plot(NA, xlim=range(pred$total_budget), ylim=c(0,1), log='x',
     xlab='Total budget B (updates; log axis)', ylab='Probability of at least one success',
     main='Restart predictions from Review 1 calibration runs')
for (i in seq_along(c(1,2,4))) {
    cell <- pred[pred$k == c(1,2,4)[i],]
    lines(cell$total_budget, cell$predicted_success, type='s', col=cols[i], lty=i, lwd=2)
}
legend('topleft', legend=c('One long run','Two independent runs','Four independent runs'),
       col=cols, lty=1:3, lwd=2, bty='n', cex=.9)
dev.off()
