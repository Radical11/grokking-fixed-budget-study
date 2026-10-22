# Base-R analysis: no contributed packages required.
# Run from the repository root: Rscript analysis/analyze.R review1
args <- commandArgs(trailingOnly=TRUE)
mode <- if(length(args)) args[1] else 'review1'
stopifnot(mode %in% c('review1','review2'))
out <- file.path('output', mode)
dir.create(out, recursive=TRUE, showWarnings=FALSE)
set.seed(20261013)
all <- read.csv('data/summary.csv', stringsAsFactors=FALSE, na.strings=c('','NA'))
x <- subset(all, stage=='main' & status=='completed')
if(!nrow(x)) stop('No completed main-study runs: do not create invented results.')
stopifnot(length(unique(x$max_updates))==1, !anyDuplicated(x$run_id))
stopifnot(length(unique(x$device))==1)
if('torch_version' %in% names(x))stopifnot(length(unique(x$torch_version))==1)
x$event_observed <- as.logical(x$event_observed)
x$delayed_generalization <- as.logical(x$delayed_generalization)
stopifnot(all(!is.na(x$event_observed)), all(x$completed_updates==x$max_updates),
          all(is.na(x$generalization_time)==!x$event_observed))
C <- unique(x$max_updates)
x$U <- ifelse(x$event_observed,x$generalization_time,C)
stopifnot(all(x$U<=C),all(x$U>0))
# Selected baseline is stored by Python; use json text only for the simple numeric fields.
selection <- paste(readLines('data/baseline.json',warn=FALSE),collapse=' ')
number <- function(key) as.numeric(sub(paste0('.*"',key,'"\\s*:\\s*([0-9.eE+-]+).*'),'\\1',selection,perl=TRUE))
baseline_wd <- number('weight_decay')
baseline_fraction <- number('train_fraction')
baseline <- subset(x, train_fraction==baseline_fraction & weight_decay==baseline_wd)
stopifnot(nrow(baseline)>0)
exact_ci <- function(success,n) unname(binom.test(success,n)$conf.int)
boot_mean <- function(u) quantile(replicate(1000,mean(sample(u,length(u),replace=TRUE))),c(.025,.975),names=FALSE)
groups <- split(x, interaction(x$train_fraction,x$weight_decay,drop=TRUE))
stats <- do.call(rbind,lapply(groups,function(g){
  ci <- exact_ci(sum(g$event_observed),nrow(g)); mci <- boot_mean(g$U)
  data.frame(train_fraction=g$train_fraction[1],weight_decay=g$weight_decay[1],n=nrow(g),
    successes=sum(g$event_observed),censored=sum(!g$event_observed),delayed=sum(g$delayed_generalization),
    success_probability=mean(g$event_observed),prob_ci_low=ci[1],prob_ci_high=ci[2],
    mean_capped_time=mean(g$U),sd_capped_time=sd(g$U),median_capped_time=median(g$U),
    mean_ci_low=mci[1],mean_ci_high=mci[2],
    median_observed_time=if(any(g$event_observed))median(g$generalization_time[g$event_observed]) else NA,
    mean_runtime_seconds=mean(g$elapsed_seconds))
}))
rownames(stats)<-NULL
write.csv(stats,file.path(out,'group_statistics.csv'),row.names=FALSE)
write.csv(x,file.path(out,'analysis_rows.csv'),row.names=FALSE)
write.csv(data.frame(main_total=sum(all$stage=='main'),completed=nrow(x),
  failed=sum(all$stage=='main' & all$status=='failed'),paused=sum(all$stage=='main' & all$status=='paused'),
  pilot_runs=sum(all$stage=='pilot'),baseline_fraction=baseline_fraction,baseline_wd=baseline_wd,cap=C),
  file.path(out,'audit_counts.csv'),row.names=FALSE)
palette <- c('#1F4E79','#A65422','#376A4F')
plot_start <- function(name,height=900) {
  png(file.path(out,paste0(name,'.png')),width=2200,height=height,res=230,pointsize=16)
  par(mar=c(3.5,if(name=='setting_comparison')6 else 4,2.5,1),mgp=c(2.5,.7,0),cex=.98,las=1,bty='l')
}

# Representative trace chosen closest to baseline median; all traces remain available.
observed <- baseline[baseline$event_observed,]
if(nrow(observed)) representative <- observed[which.min(abs(observed$generalization_time-median(observed$generalization_time))),] else representative<-baseline[1,]
trace_path <- file.path('data','runs','main',representative$run_id,'trace.csv')
trace <- read.csv(trace_path)
zoom_end <- min(C,max(1000,if(!is.na(representative$generalization_time))ceiling(representative$generalization_time*1.6/100)*100 else C))
plot_start('learning_curve')
plot(trace$step,trace$train_acc,type='l',col=palette[1],lwd=2,ylim=c(0,1.02),xlim=c(0,zoom_end),xlab='Optimizer updates (early training window)',ylab='Accuracy',
     main='Memorization and generalization in one baseline run')
lines(trace$step,trace$test_acc,col=palette[2],lwd=2)
abline(h=.95,lty=3,col='grey65')
if(!is.na(representative$memorization_time))abline(v=representative$memorization_time,lty=3,col=palette[1])
if(!is.na(representative$generalization_time))abline(v=representative$generalization_time,lty=3,col=palette[2])
legend('bottomright',c('Training pairs','Unseen pairs'),col=palette[1:2],lwd=2,bty='n')
dev.off()

plot_start('time_distribution')
times <- baseline$generalization_time[baseline$event_observed]
if(length(times)>0){
  hist(times,breaks=max(3,min(8,length(times))),col='#CEDAE5',border='white',xlab='Confirmed generalization time (updates)',
       main='Observed baseline generalization times',ylab='Number of runs')
}else{plot.new();title('No baseline runs generalized within the budget')}
dev.off()

plot_start('setting_comparison')
sixty <- subset(x,train_fraction==.6)
boxplot(U~factor(weight_decay),data=sixty,col=palette,xlab='Weight decay',ylab='',
        main='Training time capped at the common run limit')
mtext('Capped time U (updates)',side=2,line=4,las=0)
stripchart(U~factor(weight_decay),data=sixty,vertical=TRUE,method='jitter',add=TRUE,pch=16,cex=.6,col='#303030')
dev.off()

Fhat <- function(g,t) sum(g$event_observed & !is.na(g$generalization_time) & g$generalization_time<=t)/nrow(g)
grid <- seq(0,C,by=25)
plot_start('budget_probability')
plot(NA,xlim=c(0,C),ylim=c(0,1),xlab='Budget per run (updates)',ylab='Fraction generalized by budget',
     main='Probability of generalization within a budget')
for(i in seq_along(sort(unique(sixty$weight_decay)))){
  wd<-sort(unique(sixty$weight_decay))[i]; g<-subset(sixty,weight_decay==wd)
  lines(grid,sapply(grid,function(t)Fhat(g,t)),type='s',col=palette[i],lwd=2)
}
legend('bottomright',sapply(sort(unique(sixty$weight_decay)),function(wd)
  sprintf('Decay %g (n=%d)',wd,sum(sixty$weight_decay==wd))),col=palette,lwd=2,bty='n')
dev.off()

budgets <- sort(unique(c(seq(100,C,by=100),floor(C*c(.25,.5,1)/100)*100)))
predictions <- do.call(rbind,lapply(budgets,function(B){
 do.call(rbind,lapply(c(1,2,4),function(k){
  cutoff<-B/k; count<-sum(baseline$event_observed & !is.na(baseline$generalization_time) & baseline$generalization_time<=cutoff)
  p<-count/nrow(baseline); ci<-exact_ci(count,nrow(baseline))
  data.frame(total_budget=B,k=k,per_run_budget=cutoff,baseline_n=nrow(baseline),single_run_probability=p,
             predicted_success=1-(1-p)^k,ci_low=1-(1-ci[1])^k,ci_high=1-(1-ci[2])^k)
 }))
}))
write.csv(predictions,file.path(out,'policy_predictions.csv'),row.names=FALSE)
plot_start('restart_predictions')
pd<-subset(predictions,total_budget==C)
plot(NA,xlim=c(100,C),ylim=c(0,1),log='x',xlab='Total budget B (updates; log axis)',
     ylab='At least one success (probability)',main='Restart predictions - fresh-seed validation pending')
for(i in 1:3){
 q<-subset(predictions,k==c(1,2,4)[i]);lines(q$total_budget,q$predicted_success,type='s',col=palette[i],lwd=2)
}
legend('bottomright',c('One long run','Two independent runs','Four independent runs'),col=palette,lwd=2,bty='n')
dev.off()

# Descriptive and inferential output is reproducible and kept separate from report claims.
sink(file.path(out,'inference.txt'))
cat('Grokking fixed-budget analysis | mode:',mode,'\n')
cat('Randomization unit: independently initialized training run; fixed dataset split.\n')
cat('Completed main runs:',nrow(x),'| common cap:',C,'| pilot excluded.\n')
cat('U=min(T,C) is fully observed; it is not an imputation of unrestricted T.\n')
cat('Bootstrap mean intervals are percentile intervals from 1000 resamples.\n\n')
print(stats)
cat('\nBaseline capped mean and variance:',mean(baseline$U),var(baseline$U),'\n')
cat('\nExploratory comparisons at 60% data: Welch tests, bootstrap mean differences.\n')
wds<-sort(unique(sixty$weight_decay)); pair_results<-list()
for(pair in combn(wds,2,simplify=FALSE)){
 a<-subset(sixty,weight_decay==pair[1])$U;b<-subset(sixty,weight_decay==pair[2])$U
 test<-tryCatch(t.test(a,b),error=function(e)NULL)
 diffci<-quantile(replicate(1000,mean(sample(a,length(a),TRUE))-mean(sample(b,length(b),TRUE))),c(.025,.975))
 cat('Decays',pair[1],'vs',pair[2],'| difference:',mean(a)-mean(b),'| bootstrap CI:',diffci,'\n')
 if(!is.null(test)){print(test);pair_results[[length(pair_results)+1]]<-data.frame(wd_a=pair[1],wd_b=pair[2],p=test$p.value)}
}
if(length(pair_results)){
 pr<-do.call(rbind,pair_results);pr$p_holm<-p.adjust(pr$p,'holm');print(pr)
 write.csv(pr,file.path(out,'welch_tests.csv'),row.names=FALSE)
}
cat('\nOne-way ANOVA (exploratory):\n')
one<-lm(U~factor(weight_decay),data=sixty);print(anova(one))
cat('Residual diagnostics; capped outcomes may violate normality:\n')
if(sd(residuals(one))>0 && length(residuals(one))>=3 && length(residuals(one))<=5000)print(shapiro.test(residuals(one)))
if(length(unique(sixty$U))>1){
 f_obs<-anova(one)$`F value`[1]
 f_perm<-replicate(1000,{q<-sixty;q$U<-sample(q$U);anova(lm(U~factor(weight_decay),data=q))$`F value`[1]})
 cat('Permutation sensitivity p:',(1+sum(f_perm>=f_obs,na.rm=TRUE))/1001,'\n')
}
cat('\nSimple correlation and regression of U on log(weight decay):\n')
if(sd(sixty$U)>0){
 print(cor.test(log(sixty$weight_decay),sixty$U,method='pearson'))
 print(cor.test(sixty$weight_decay,sixty$U,method='spearman',exact=FALSE))
 print(summary(lm(U~log(weight_decay),data=sixty)))
}
if(mode=='review2' && length(unique(x$train_fraction))==2){
 cat('\nMultiple regression:\n'); multiple<-lm(U~train_fraction+log(weight_decay),data=x);print(summary(multiple))
 cat('\nTwo-factor ANOVA, with interaction:\n')
 two<-lm(U~factor(train_fraction)*factor(weight_decay),data=x);print(anova(two))
 cat('Residuals vs fitted, QQ plot and group variance plots must be inspected before strong inference.\n')
 plot_start('model_diagnostics',1600);par(mfrow=c(2,2));plot(two);dev.off()
}
cat('\nNo F variance test or chi-square goodness-of-fit forced onto sparse/capped samples.\n')
cat('Each policy prediction uses estimated F, conditional independence of initialization seeds and a fixed split.\n')
cat('Predictions across budgets are correlated; they are not independent experimental replicates.\n')
sink()

# Discretized continuous-family likelihood for known confirmation times.
# Confirmation adds two evaluation intervals (50 updates); modeled X is T-50.
# P(T=t) = F_X(t-50)-F_X(t-75). Unfinished runs contribute P(T>C).
if(mode=='review2' && sum(baseline$event_observed)>=8){
 t<-baseline$generalization_time; event<-baseline$event_observed
 cdf<-function(v,par,distribution){
  v<-pmax(0,v-50)
  if(distribution=='Exponential')pexp(v,rate=exp(par[1])) else
  if(distribution=='Gamma')pgamma(v,shape=exp(par[1]),scale=exp(par[2])) else
    pweibull(v,shape=exp(par[1]),scale=exp(par[2]))
 }
 results<-list(); fits<-list()
 for(distribution in c('Exponential','Gamma','Weibull')){
  initial<-if(distribution=='Exponential')log(1/(median(t[event])-50)) else log(c(2,(median(t[event])-50)/2))
  nll<-function(par){
   prob<-cdf(t[event],par,distribution)-cdf(pmax(0,t[event]-25),par,distribution)
   surv<-1-cdf(C,par,distribution)
   -sum(log(pmax(prob,1e-300)))-sum(!event)*log(pmax(surv,1e-300))
  }
  if(distribution=='Exponential'){
   opt<-optimize(nll,interval=log(c(1/(C*1000),1)))
   fit<-list(par=opt$minimum,value=opt$objective,convergence=0)
  }else fit<-optim(initial,nll,method='Nelder-Mead',control=list(maxit=3000))
  results[[distribution]]<-data.frame(distribution=distribution,converged=fit$convergence==0,
    parameter_1=exp(fit$par[1]),parameter_2=if(length(fit$par)>1)exp(fit$par[2]) else NA,
    negative_log_likelihood=fit$value,AIC=2*length(fit$par)+2*fit$value)
  fits[[distribution]]<-fit
 }
 write.csv(do.call(rbind,results),file.path(out,'distribution_fits.csv'),row.names=FALSE)
 plot_start('distribution_fits')
 plot(grid,sapply(grid,function(v)Fhat(baseline,v)),type='s',ylim=c(0,1),lwd=2,xlab='Updates',ylab='Probability generalized',main='Baseline event-time models with unfinished runs retained')
 for(i in 1:3)lines(grid,cdf(grid,fits[[i]]$par,names(fits)[i]),col=palette[i],lty=2,lwd=2)
 legend('bottomright',c('Observed',names(fits)),col=c('black',palette),lty=c(1,2,2,2),bty='n')
 dev.off()
}
if(mode=='review2' && file.exists('data/policies.csv')){
 pol<-read.csv('data/policies.csv');pol$success<-as.logical(pol$success)
 stopifnot(all(pol$allocated_updates==pol$total_budget),all(pol$completed_updates==pol$total_budget))
 ps<-do.call(rbind,lapply(split(pol,pol$k),function(g){ci<-exact_ci(sum(g$success),nrow(g));
  data.frame(k=g$k[1],attempts=nrow(g),successes=sum(g$success),observed_probability=mean(g$success),
   ci_low=ci[1],ci_high=ci[2],mean_runtime_seconds=mean(g$elapsed_seconds))}))
 write.csv(ps,file.path(out,'policy_validation.csv'),row.names=FALSE)
 plot_start('policy_validation')
 plot(ps$k,ps$observed_probability,ylim=c(0,1),xaxt='n',xlab='Number of independent runs',ylab='Probability of at least one success',main='Fresh-seed policy validation',pch=16,col=palette[1])
 axis(1,ps$k,ps$k);arrows(ps$k,ps$ci_low,ps$k,ps$ci_high,code=3,angle=90,length=.08,col=palette[1])
 points(pd$k,pd$predicted_success,pch=1,col=palette[2],cex=1.3)
 legend('bottomright',c('Observed (exact 95% CI)','Predicted from main runs'),pch=c(16,1),col=palette[1:2],bty='n');dev.off()
 sink(file.path(out,'policy_tests.txt'))
 tab<-table(pol$k,pol$success)
 print(tab)
 if(ncol(tab)==2){
  chi<-suppressWarnings(chisq.test(tab))
  if(all(chi$expected>=5))print(chi) else {cat('Expected counts below 5; use Fisher exact test.\n');print(fisher.test(tab))}
 }else cat('All outcomes identical; no evidence for a policy difference.\n')
 cat('Ten attempts per policy give wide intervals. Absence of significance is not evidence of equivalence.\n')
 sink()
}
writeLines(c('Analysis completed by R',paste('R version:',R.version.string),paste('Completed main runs:',nrow(x)),
             paste('Baseline n:',nrow(baseline)),paste('Representative trace:',representative$run_id)),file.path(out,'validation.txt'))
cat('R analysis complete:',nrow(x),'main runs; outputs in',out,'\n')
