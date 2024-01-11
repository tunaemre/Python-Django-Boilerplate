from types import SimpleNamespace

todo_scope = SimpleNamespace(
    read='read:todo',
    write='write:todo'
)

admin_scope = SimpleNamespace(
    admin='admin'
)

worker_scope = SimpleNamespace(
    worker='worker'
)
