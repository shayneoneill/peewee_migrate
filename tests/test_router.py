""" Tests for `peewee_migrate` module. """
import peewee as pw
import os
import mock


def test_router():
    from peewee_migrate import MigrateHistory
    from peewee_migrate.cli import get_router

    router = get_router('tests/migrations', 'sqlite:///:memory:')

    assert router.database
    assert isinstance(router.database, pw.Database)

    assert router.todo == ['001_test', '002_test', '003_tespy']
    assert router.done == []
    assert router.diff == ['001_test', '002_test', '003_tespy']

    router.create('new')
    assert router.todo == ['001_test', '002_test', '003_tespy', '004_new']
    os.remove('tests/migrations/004_new.py')

    MigrateHistory.create(name='001_test')
    assert router.diff == ['002_test', '003_tespy']

    MigrateHistory.delete().execute()

    router.run()
    assert router.diff == []

    with mock.patch('peewee.Database.execute_sql') as execute_sql:
        router.run_one('002_test', router.migrator, fake=True)

    assert not execute_sql.called

    migrations = MigrateHistory.select()
    assert list(migrations)
    assert migrations.count() == 3

    router.rollback('003_tespy')
    assert router.diff == ['003_tespy']
    assert migrations.count() == 2

    with mock.patch('os.remove') as mocked:
        router.merge()
        assert mocked.call_count == 3
        assert mocked.call_args[0][0] == 'tests/migrations/003_tespy.py'
        assert MigrateHistory.select().count() == 1

    os.remove('tests/migrations/001_initial.py')

# pylama:ignore=W0621
