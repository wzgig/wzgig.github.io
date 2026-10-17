---
title: From a physical model to an equivalent circuit
description: A short guide to the modeling workflow behind my work on PMSG impedance and admittance prediction.
date: 2026-10-18
category: Research notes
publish: true
sensitive: false
---
An impedance curve tells us how a device responds to a small disturbance over frequency. An equivalent circuit offers another way to describe that response: as a combination of circuit elements. My work on permanent-magnet synchronous generators (PMSGs) connects these two views, then explores how the representation changes with the operating point.

This note introduces the workflow. It is a conceptual overview, rather than an independent validation or a reproduction of the published results.

## 1. Start with the operating point

A small-signal model describes behavior around an equilibrium. Before linearizing the electrical and control equations, the operating point and the variables held fixed need to be clear. Changing the operating point can change the resulting frequency response.

The model is local: a useful linear approximation around one equilibrium does not, by itself, describe large disturbances or all other operating conditions.

## 2. Move into the frequency domain

Linearization gives a state-space description. With appropriate inputs and outputs, this can be transformed into an impedance or admittance matrix. In a rotating reference frame, the off-diagonal terms represent coupling between axes; interpreting a single element requires remembering the matrix it belongs to.

I keep a public repository for [PMSG electrical modeling and linearization](https://github.com/wzgig/pmsg-electrical-model-linearization), and another for the path from [state-space models to vector fitting and equivalent circuits](https://github.com/wzgig/Vector-fitting-and-equivalent-circuit-transformation).

## 3. Fit a compact representation

Vector fitting approximates a frequency response with a rational function. That representation can be related to circuit elements. A reduced circuit gives a smaller set of quantities to inspect and, potentially, predict.

Two distinctions matter here. A fitted response is an approximation over a chosen frequency range, and an equivalent circuit is a representation of terminal behavior. Its elements should not automatically be interpreted as a one-to-one map of the physical components inside the device.

## 4. Learn how the representation varies

Instead of learning every sampled frequency response directly, one can investigate predicting parameters of the reduced representation across operating points. My first-author journal paper studies this direction using support vector machines:

> Admittance Prediction for PMSG via Dimensionality-Reduced Equivalent Circuits and Support Vector Machines. *Technologies*, 2026, 14(6), 323.

The [publisher’s version](https://www.mdpi.com/2227-7080/14/6/323) contains the method, experiments, and their specific scope. My [ACPEE 2026 paper](https://ieeexplore.ieee.org/document/11524472) addresses impedance prediction in circuit form under variable operating points.

## What I want to keep checking

For this kind of workflow, I find three questions useful:

- Does the approximation preserve the frequency behavior that matters for the intended analysis?
- How well does the prediction hold at operating points outside the training samples?
- Which physical insights survive the reduction, and which require returning to the original model?

A compact model is most useful when its assumptions and limits remain visible. That is the connection between physical modeling and machine learning that I want to keep exploring.
