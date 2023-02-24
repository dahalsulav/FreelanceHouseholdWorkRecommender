from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Recommendation, WorkerSkillset, Skillset


@login_required
def recommend_worker(request, task_id):
    task = Task.objects.get(id=task_id)
    skillsets = task.skillset.all()

    # Find all workers who have the required skillsets
    workers = User.objects.filter(is_worker=True)
    for skillset in skillsets:
        workers = workers.filter(worker_skillset__skillset=skillset)

    # Score each worker based on their skillset and hourly rate
    recommendations = []
    for worker in workers:
        worker_skillsets = WorkerSkillset.objects.filter(worker=worker)
        score = 0
        for task_skillset in skillsets:
            if worker_skillsets.filter(skillset=task_skillset).exists():
                score += 1
        score /= len(skillsets)
        score *= 1 - (worker.worker.hourly_rate / task.price)
        recommendation = Recommendation(worker=worker, task=task, score=score)
        recommendations.append(recommendation)
        recommendation.save()

    # Sort the recommendations by score in descending order
    recommendations = sorted(recommendations, key=lambda r: r.score, reverse=True)

    return render(
        request, "recommend_worker.html", {"recommendations": recommendations}
    )


@login_required
def recommend_task(request, worker_id):
    worker = User.objects.get(id=worker_id)
    worker_skillsets = WorkerSkillset.objects.filter(worker=worker)

    # Find all tasks that require the worker's skillset
    tasks = Task.objects.all()
    for worker_skillset in worker_skillsets:
        tasks = tasks.filter(skillset=worker_skillset.skillset)

    # Score each task based on how many of the worker's skillsets are required
    recommendations = []
    for task in tasks:
        task_skillsets = task.skillset.all()
        score = 0
        for worker_skillset in worker_skillsets:
            if task_skillsets.filter(id=worker_skillset.skillset.id).exists():
                score += 1
        score /= len(worker_skillsets)
        recommendation = Recommendation(worker=worker, task=task, score=score)
        recommendations.append(recommendation)
        recommendation.save()

    # Sort the recommendations by score in descending order
    recommendations = sorted(recommendations, key=lambda r: r.score, reverse=True)

    return render(request, "recommend_task.html", {"recommendations": recommendations})
