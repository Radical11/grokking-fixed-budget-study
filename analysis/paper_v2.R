# Base-R analysis for the pre-specified paper-v2 follow-up. Original analysis is unchanged.
analyze_paper <- function(data_dir='data/paper_v2', out='output/paper_v2', legacy='output/review2', figures=TRUE) {
  dir.create(out,recursive=TRUE,showWarnings=FALSE)
  set.seed(20261015)
  read <- function(name) read.csv(file.path(data_dir,name),stringsAsFactors=FALSE,na.strings=c('','NA'))
  write <- function(x,name) write.csv(x,file.path(out,paste0(name,'.csv')),row.names=FALSE)
  runs<-read('run_summary.csv'); attempts<-read('attempt_summary.csv'); frozen<-read('frozen_predictions.csv')
  stopifnot(nrow(runs)==1350,all(runs$status=='completed'),nrow(attempts)==540,all(attempts$status=='completed'))
  stopifnot(all(attempts$completed_updates==attempts$total_budget),all(attempts$allocated_updates==attempts$total_budget))
  cal<-subset(runs,cohort=='calibration');stopifnot(nrow(cal)==90,all(table(cal$split_seed)==30))
  stopifnot(all(table(interaction(attempts$split_seed,attempts$total_budget,attempts$k))==30))
  for(ep in c('first','stability')) {
    cal[[paste0(ep,'_event')]]<-as.logical(cal[[paste0(ep,'_event')]])
    attempts[[paste0(ep,'_success')]]<-as.logical(attempts[[paste0(ep,'_success')]])
    stopifnot(all(is.na(cal[[paste0(ep,'_time')]])==!cal[[paste0(ep,'_event')]]))
    stopifnot(!anyNA(attempts[[paste0(ep,'_success')]]))
  }
  stopifnot(all(!cal$stability_event | (cal$first_event & cal$stability_time>=cal$first_time)),
            all(!attempts$stability_success | attempts$first_success))
  cap<-30000; resamples<-5000; splits<-sort(unique(cal$split_seed))
  ci<-function(s,n,level=.95) unname(binom.test(s,n,conf.level=level)$conf.int)
  ci_cache<-sapply(0:30,function(s)ci(s,30))
  qci<-function(x)unname(quantile(x,c(.025,.975)))
  Fhat<-function(g,t,ep='first')sum(g[[paste0(ep,'_event')]] & !is.na(g[[paste0(ep,'_time')]]) & g[[paste0(ep,'_time')]]<=t)/nrow(g)
  calibration_stats<-list();curves<-list()
  for(split in splits) {
    g<-subset(cal,split_seed==split)
    for(ep in c('first','stability')) {
      event<-g[[paste0(ep,'_event')]]; t<-g[[paste0(ep,'_time')]];u<-ifelse(event,t,cap);n<-length(u)
      mci<-qci(replicate(resamples,mean(sample(u,n,replace=TRUE))));pci<-ci(sum(event),n)
      calibration_stats[[length(calibration_stats)+1]]<-data.frame(split_seed=split,endpoint=ep,n=n,events=sum(event),censored=sum(!event),
        mean_U=mean(u),median_U=median(u),sd_U=sd(u),mean_ci_low=mci[1],mean_ci_high=mci[2],probability=mean(event),ci_low=pci[1],ci_high=pci[2])
      for(time in seq(0,cap,25)) {
        successes<-sum(event & !is.na(t) & t<=time)
        curves[[length(curves)+1]]<-data.frame(split_seed=split,endpoint=ep,time=time,n=n,successes=successes,
           probability=successes/n,ci_low=ci_cache[1,successes+1],ci_high=ci_cache[2,successes+1])
      }
    }
  }
  cs<-do.call(rbind,calibration_stats);cdf<-do.call(rbind,curves);write(cs,'calibration_statistics');write(cdf,'completion_curves')
  write(cal,'calibration_rows');write(attempts,'validation_attempts')
  comparison<-list();risks<-list()
  for(split in splits)for(B in c(8000,12000))for(ep in c('first','stability')) {
    cg<-subset(cal,split_seed==split);times<-cg[[paste0(ep,'_time')]]
    one<-subset(attempts,split_seed==split & total_budget==B & k==1)[[paste0(ep,'_success')]]
    for(kval in c(1,2,4)) {
      observed<-subset(attempts,split_seed==split & total_budget==B & k==kval)[[paste0(ep,'_success')]]
      n<-length(observed);stopifnot(n==30)
      p<-Fhat(cg,B/kval,ep); predicted<-1-(1-p)^kval
      old<-subset(frozen,split_seed==split & total_budget==B & k==kval & endpoint==ep)
      stopifnot(nrow(old)==1,abs(old$predicted_success-predicted)<1e-12)
      pc<-ci(round(p*30),30); pc<-1-(1-pc)^kval; oc<-ci(sum(observed),n)
      pc_joint<-1-(1-ci(round(p*30),30,.975))^kval;oc_joint<-ci(sum(observed),n,.975)
      differences<-replicate(resamples,{
        tb<-sample(times,length(times),replace=TRUE);fb<-mean(!is.na(tb) & tb<=B/kval)
        (1-(1-fb)^kval)-mean(sample(observed,n,replace=TRUE))
      });dc<-qci(differences)
      comparison[[length(comparison)+1]]<-data.frame(split_seed=split,total_budget=B,k=kval,endpoint=ep,n=n,successes=sum(observed),
        observed_probability=mean(observed),ci_low=oc[1],ci_high=oc[2],predicted_probability=predicted,
        predicted_ci_low=pc[1],predicted_ci_high=pc[2],prediction_minus_observation=predicted-mean(observed),
        difference_ci_low=dc[1],difference_ci_high=dc[2],
        conservative_difference_ci_low=pc_joint[1]-oc_joint[2],conservative_difference_ci_high=pc_joint[2]-oc_joint[1])
      if(kval!=1) {
        rc<-qci(replicate(resamples,mean(sample(observed,n,replace=TRUE))-mean(sample(one,length(one),replace=TRUE))))
        tab<-rbind(c(sum(observed),sum(!observed)),c(sum(one),sum(!one)))
        identical<-sum(tab[,1])==0 || sum(tab[,2])==0
        pv<-if(identical)1 else fisher.test(tab,alternative='two.sided')$p.value
        restart_ci<-ci(sum(observed),n,.975);long_ci<-ci(sum(one),length(one),.975)
        risks[[length(risks)+1]]<-data.frame(split_seed=split,total_budget=B,k=kval,endpoint=ep,n_restart=n,n_long=length(one),
          risk_difference=mean(observed)-mean(one),ci_low=rc[1],ci_high=rc[2],
          conservative_ci_low=restart_ci[1]-long_ci[2],conservative_ci_high=restart_ci[2]-long_ci[1],p_value=if(ep=='first')pv else NA_real_,
          method=if(ep=='stability')'Secondary descriptive' else if(identical)'All outcomes identical; descriptive p=1' else 'Two-sided Fisher exact')
      }
    }
  }
  ps<-do.call(rbind,comparison);rd<-do.call(rbind,risks);rd$p_holm<-NA_real_
  primary<-which(rd$endpoint=='first');stopifnot(length(primary)==12)
  rd$p_holm[primary]<-p.adjust(rd$p_value[primary],method='holm')
  write(ps,'policy_statistics');write(rd,'risk_differences')
  model_cdf<-function(t,par,dist) {
    z<-pmax(0,t-50)
    if(dist=='Exponential')pexp(z,rate=exp(par[1])) else if(dist=='Gamma')pgamma(z,shape=exp(par[1]),scale=exp(par[2])) else pweibull(z,shape=exp(par[1]),scale=exp(par[2]))
  }
  base<-subset(cal,split_seed==20261013);event<-base$first_event;t<-base$first_time;fits<-list();fit_rows<-list()
  if(sum(event)>=8)for(dist in c('Exponential','Gamma','Weibull')) {
    nll<-function(par) {
      mass<-model_cdf(t[event],par,dist)-model_cdf(t[event]-25,par,dist)
      survival<-1-model_cdf(cap,par,dist)
      -sum(log(pmax(mass,1e-300)))-sum(!event)*log(pmax(survival,1e-300))
    }
    initial<-if(dist=='Exponential')log(1/(median(t[event])-50)) else log(c(2,(median(t[event])-50)/2))
    if(dist=='Exponential') {opt<-optimize(nll,interval=log(c(1/(cap*1000),1)));fit<-list(par=opt$minimum,value=opt$objective,convergence=0)}
    else fit<-optim(initial,nll,method='Nelder-Mead',control=list(maxit=3000))
    fits[[dist]]<-fit
    fit_rows[[dist]]<-data.frame(distribution=dist,n=nrow(base),events=sum(event),censored=sum(!event),converged=fit$convergence==0,
      parameter_1=exp(fit$par[1]),parameter_2=if(length(fit$par)>1)exp(fit$par[2]) else NA,negative_log_likelihood=fit$value,AIC=2*length(fit$par)+2*fit$value)
  }
  if(length(fit_rows))write(do.call(rbind,fit_rows),'distribution_fits')
  candidates<-base[base$first_event,]; representative<-candidates[which.min(abs(candidates$first_time-median(candidates$first_time))),]
  write(representative,'representative_run')
  counts<-data.frame(calibration=90,reused_calibration=20,new_calibration=70,validation_attempts=540,validation_constituents=1260,
     new_training_runs=1330,new_logical_updates=7500000,primary_tests=12,bootstrap_resamples=resamples)
  write(counts,'study_counts')
  if(figures) {
    palette<-c('#175F96','#637E8E','#253F50')
    plot_file<-function(name,draw,width=7.6,height=4.6) {
      png(file.path(out,paste0(name,'.png')),width=round(width*300),height=round(height*300),res=300,pointsize=11)
      par(mar=c(4.2,4.7,3.1,1),mgp=c(2.7,.75,0),bty='l',las=1);draw();dev.off()
      pdf(file.path(out,paste0(name,'.pdf')),width=width,height=height,pointsize=11,useDingbats=FALSE)
      par(mar=c(4.2,4.7,3.1,1),mgp=c(2.7,.75,0),bty='l',las=1);draw();dev.off()
    }
    plot_file('learning_delay',function(){
      par(mfrow=c(2,1),mar=c(3.4,4.7,2.3,1),mgp=c(2.35,.65,0),cex=1)
      trace<-read.csv(file.path(as.character(representative$source_path),'trace.csv'))
      zoom<-min(cap,max(1000,ceiling(1.6*representative$first_time/100)*100))
      plot(trace$step,trace$train_acc,type='l',col=palette[1],lwd=2,ylim=c(0,1.03),xlim=c(0,zoom),xlab='Optimizer updates',ylab='Accuracy',main='Practice improves before held-out performance')
      lines(trace$step,trace$test_acc,col=palette[2],lwd=2);abline(h=.95,lty=3,col='grey65')
      abline(v=representative$first_time,col=palette[1],lty=3)
      if(!is.na(representative$stability_time))abline(v=representative$stability_time,col=palette[2],lty=2)
      legend('bottomright',c('Practice pairs','Held-out pairs','First confirmation','500-update confirmation'),col=palette[c(1,2,1,2)],lwd=c(2,2,1,1),lty=c(1,1,3,2),bty='n',cex=.85)
      plot(0,0,type='n',xlim=c(0,cap),ylim=c(0,1),xlab='Optimizer updates',ylab='Probability confirmed',main='Completion curves: 30 calibration runs per split')
      for(i in 1:3){g<-subset(cdf,split_seed==splits[i] & endpoint=='first');lines(g$time,g$probability,type='s',col=palette[i],lwd=2,lty=i)}
      legend('bottomright',paste('Split',1:3),col=palette,lty=1:3,lwd=2,bty='n',cex=.85)
    },height=6.4)
    plot_file('timing_variation',function(){
      par(mar=c(4.2,6,3.1,1),mgp=c(2.7,.75,0))
      u<-ifelse(cal$first_event,cal$first_time,cap);grp<-factor(cal$split_seed,levels=splits)
      boxplot(u~grp,outline=FALSE,col='white',border=palette,xaxt='n',ylim=c(0,31000),xlab='Fixed dataset split (n = 30 each)',ylab='',main='Timing variation across three fixed splits')
      mtext('Capped time U (updates)',side=2,line=4.3,las=0)
      axis(1,1:3,paste('Split',1:3));set.seed(20261015)
      points(as.numeric(grp)+runif(length(u),-.12,.12),u,pch=ifelse(cal$first_event,16,2),col=palette[as.numeric(grp)],cex=.65)
      legend('topright',c('Observed event','Unfinished at cap'),pch=c(16,2),bty='n',cex=.85)
    })
    plot_file('completion_curves',function(){
      plot(0,0,type='n',xlim=c(0,cap),ylim=c(0,1),xlab='Optimizer updates',ylab='Probability of first confirmation',main='Calibration completion curves (n = 30 per split)')
      for(i in 1:3){g<-subset(cdf,split_seed==splits[i] & endpoint=='first');lines(g$time,g$probability,type='s',col=palette[i],lwd=2,lty=i)}
      legend('bottomright',paste('Split',1:3),col=palette,lty=1:3,lwd=2,bty='n')
    })
    plot_file('policy_validation',function(){
      par(mfrow=c(2,3),mar=c(3.5,3.4,2.5,.6),oma=c(1.5,1.5,1.4,0),mgp=c(2.1,.65,0),cex=1)
      for(B in c(8000,12000))for(split in splits){
        g<-subset(ps,endpoint=='first' & split_seed==split & total_budget==B);g<-g[order(g$k),]
        observed_x<-(1:3)-.06;predicted_x<-(1:3)+.06
        plot(observed_x,g$observed_probability,pch=16,col=palette[1],ylim=c(0,1.05),xlim=c(.7,3.3),xaxt='n',xlab='Runs per attempt',ylab='Success probability',main=paste('Split',match(split,splits),'| B =',format(B,big.mark=',')),cex.main=.9)
        axis(1,1:3,c(1,2,4));arrows(observed_x,g$ci_low,observed_x,g$ci_high,code=3,angle=90,length=.04,col=palette[1])
        arrows(predicted_x,g$predicted_ci_low,predicted_x,g$predicted_ci_high,code=3,angle=90,length=.04,col=palette[2]);points(predicted_x,g$predicted_probability,pch=1,col=palette[2])
      }
      mtext('Filled: observed | Open: frozen prediction | Pointwise 95% intervals; separate n = 30 samples',side=1,outer=TRUE,line=.3,cex=.8)
    },height=6)
    plot_file('risk_differences',function(){
      g<-subset(rd,endpoint=='first');labels<-paste0('S',match(g$split_seed,splits),' / ',g$total_budget/1000,'k / ',g$k,' vs 1');y<-rev(seq_len(nrow(g)))
      par(mar=c(4.2,7,3.1,1));plot(g$risk_difference,y,xlim=c(-1,1),ylim=c(.5,length(y)+.5),yaxt='n',pch=16,col=palette[1],xlab='Success probability difference (restart - one run)',ylab='',main='Policy differences; conservative pointwise 95% intervals')
      axis(2,y,labels,cex.axis=.9);segments(g$conservative_ci_low,y,g$conservative_ci_high,y,col=palette[1]);abline(v=0,col='grey65',lty=2)
    },height=5.4)
    plot_file('stability_comparison',function(){
      par(mfrow=c(2,3),mar=c(3.5,3.4,2.5,.6),oma=c(1.5,1.5,1.4,0),mgp=c(2.1,.65,0),cex=1)
      for(B in c(8000,12000))for(split in splits){
        a<-subset(ps,endpoint=='first' & split_seed==split & total_budget==B);a<-a[order(a$k),]
        b<-subset(ps,endpoint=='stability' & split_seed==split & total_budget==B);b<-b[order(b$k),]
        plot((1:3)-.06,a$observed_probability,pch=16,col=palette[1],ylim=c(0,1.05),xlim=c(.7,3.3),xaxt='n',xlab='Runs per attempt',ylab='Success probability',main=paste('Split',match(split,splits),'| B =',format(B,big.mark=',')),cex.main=.9)
        axis(1,1:3,c(1,2,4));arrows((1:3)-.06,a$ci_low,(1:3)-.06,a$ci_high,code=3,angle=90,length=.035,col=palette[1]);points((1:3)+.06,b$observed_probability,pch=2,col=palette[2]);arrows((1:3)+.06,b$ci_low,(1:3)+.06,b$ci_high,code=3,angle=90,length=.035,col=palette[2])
      }
      mtext('Circle: first confirmation | Triangle: 500-update window | Exact 95% CI, n = 30',side=1,outer=TRUE,line=.3,cex=.8)
    },height=6)
    if(length(fits))plot_file('distribution_fits',function(){
      grid<-seq(0,cap,25);g<-subset(cdf,split_seed==20261013 & endpoint=='first')
      plot(g$time,g$probability,type='s',lwd=2,xlab='Optimizer updates',ylab='Probability of first confirmation',ylim=c(0,1),main='Three timing candidates; original split calibration (n = 30)')
      for(i in seq_along(fits))lines(grid,model_cdf(grid,fits[[i]]$par,names(fits)[i]),col=palette[i],lty=i+1,lwd=2)
      legend('bottomright',c('Empirical',names(fits)),col=c('black',palette),lty=1:4,lwd=2,bty='n',cex=.85)
    })
    old<-read.csv(file.path(legacy,'analysis_rows.csv'))
    plot_file('legacy_settings',function(){
      par(mar=c(4.2,6,3.1,1),mgp=c(2.7,.75,0))
      group<-factor(paste0(old$train_fraction,' / ',old$weight_decay),levels=c('0.4 / 0.3','0.4 / 1','0.4 / 3','0.6 / 0.3','0.6 / 1','0.6 / 3'))
      boxplot(old$U~group,col='white',border=palette[1],ylim=c(0,31000),xlab='Training fraction / weight decay (n = 20 per cell)',ylab='',main='Original setting study: 120 main runs',cex.axis=.85)
      mtext('Capped time U (updates)',side=2,line=4.3,las=0)
    })
  }
  writeLines(c('Paper-v2 R analysis complete',R.version.string,'Calibration: 90 (20 reused); validation attempts: 540',
    'Primary Fisher comparisons: 12, Holm family; stability descriptive',
    'Bootstrap intervals: pointwise; calibration and validation independently resampled',
    'First confirmation and finite-window stability are distinct; no equivalence inference'),file.path(out,'analysis_validation.txt'))
  cat('Paper-v2 analysis complete: 90 calibration rows; 540 policy attempts; outputs:',out,'\n')
  invisible(list(calibration=cs,policies=ps,risks=rd))
}

if(sys.nframe()==0L){
 args<-commandArgs(trailingOnly=TRUE)
 analyze_paper(if(length(args)>=1)args[1] else 'data/paper_v2',if(length(args)>=2)args[2] else 'output/paper_v2',figures=!('--no-figures'%in%args))
}
