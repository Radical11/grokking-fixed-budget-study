import pytest
from grokking.protocol import Detector, allocate_budget, success_probability


def test_confirmation_and_reset():
    d=Detector()
    for step,tr,te in [(25,1.,.96),(50,1.,.94),(75,1.,.97),(100,1.,.98)]:
        d.observe(step,tr,te)
    assert d.memorization_time==75 and d.generalization_time is None
    d.observe(125,1.,.99)
    assert d.generalization_time==125
    d.observe(150,1.,.8)
    assert d.relapsed


def test_both_thresholds_required():
    d=Detector()
    for step in [25,50,75]:d.observe(step,.98,1.)
    assert d.generalization_time is None


def test_censoring_and_delayed_label():
    d=Detector()
    for step in [25,50,75]:d.observe(step,1.,.1)
    assert d.generalization_time is None and not d.delayed()
    for step in [500,525,550]:d.observe(step,1.,1.)
    assert d.delayed()


@pytest.mark.parametrize('budget',[30000,60000])
@pytest.mark.parametrize('k',[1,2,4])
def test_budget_accounting(budget,k):
    assert sum(allocate_budget(budget,k))==budget
    assert len(allocate_budget(budget,k))==k


def test_invalid_budget():
    with pytest.raises(ValueError):allocate_budget(301,4)
    assert success_probability(.5,4)==.9375
    assert success_probability(0,4)==0
    assert success_probability(1,4)==1
