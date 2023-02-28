from django.shortcuts import render


class TaskCreateView(CreateView):
    """
    A view for creating a new task.

    Allows a customer to create a new task, selecting a worker from a list of
    available workers.

    Parameters:
    - CreateView (class): Django generic view for creating objects in the database.
    """

    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/create.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        """
        Called when a valid form is submitted.

        Sets the task status to "requested" and sends a message to the user to confirm
        the task creation.

        Parameters:
        - form (TaskCreateForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the success URL with a success message.
        """
        task = form.save(commit=False)
        task.customer = self.request.user.customer
        task.status = Task.Status.REQUESTED
        task.save()
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)


class TaskListView(ListView):
    """
    A view for displaying a list of tasks.

    Allows a customer to view a list of their tasks and their associated worker and status.

    Parameters:
    - ListView (class): Django generic view for displaying a list of objects.
    """

    model = Task
    template_name = "tasks/list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        """
        Gets the queryset of tasks to be displayed.

        Returns:
        - QuerySet: The queryset of tasks to be displayed.
        """
        customer = self.request.user.customer
        return Task.objects.filter(customer=customer).order_by("-created_at")


class TaskAcceptView(View):
    """
    A view for allowing a worker to accept a task.

    Allows a worker to accept a task, updating the task status to "in progress".

    Parameters:
    - View (class): Django generic view for handling HTTP requests.
    """

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to the view.

        Updates the task status to "in progress" and sends a message to the customer to
        confirm the task acceptance.

        Parameters:
        - request (HttpRequest): The HTTP request.
        - args: Additional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - HttpResponse: A redirect to the task detail page with a success message.
        """
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        worker = request.user.worker

        if task.worker or task.status != Task.Status.REQUESTED:
            messages.error(request, "This task cannot be accepted.")
            return redirect("task_detail", pk=task.pk)

        task.worker = worker
        task.status = Task.Status.IN_PROGRESS
