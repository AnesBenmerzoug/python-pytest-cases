import pytest

from pytest_cases import parametrize_plus, lazy_value


def valtuple():
    return 1, 2


def val():
    return 1


has_pytest_param = hasattr(pytest, 'param')
if not has_pytest_param:
    @parametrize_plus("a", [lazy_value(val),
                            lazy_value(val, id='A')])
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a == 1


    @parametrize_plus("a,b", [lazy_value(valtuple),
                              (1, lazy_value(val))])
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        assert (a, b) == (1, 2) or (a, b) == (1, 1)


    def test_synthesis(module_results_dct):
        assert list(module_results_dct) == ['test_foo_single[val]',
                                            'test_foo_single[A]',
                                            'test_foo_multi[a0-b0]',  # normal: lazy_value is used for the whole tuple
                                                                      # AND we cannot use pytest.param in this version
                                                                      # AND there are no fixtures so we pass to normal @parametrize
                                            'test_foo_multi[1-val]']

else:
    @parametrize_plus("a", [lazy_value(val),
                            pytest.param(lazy_value(val), id='B'),
                            pytest.param(lazy_value(val, id='ignored'), id='C'),
                            lazy_value(val, id='A')])
    def test_foo_single(a):
        """here the fixture is used for both parameters at the same time"""
        assert a == 1

    flag = False

    def valtuple_only_right_when_lazy():
        global flag
        if flag:
            return 0, -1
        else:
            raise ValueError("not yet ready ! you should call me later ")

    def valtuple_toskip():
        return 15, 2


    @parametrize_plus("a,b", [lazy_value(valtuple),
                              pytest.param(lazy_value(valtuple_only_right_when_lazy), id='A'),
                              pytest.param(lazy_value(valtuple_toskip), id='Wrong', marks=pytest.mark.skip),
                              (1, lazy_value(val)),
                              pytest.param(1, lazy_value(val), id='B')])
    def test_foo_multi(a, b):
        """here the fixture is used for both parameters at the same time"""
        global flag
        flag = True
        assert (a, b) in [(1, 2), (1, 1), (0, -1)]


    def test_synthesis2(module_results_dct):
        assert list(module_results_dct) == ['test_foo_single[val]',
                                            'test_foo_single[B]',
                                            'test_foo_single[C]',
                                            'test_foo_single[A]',
                                            'test_foo_multi[valtuple]',
                                            'test_foo_multi[A]',
                                            'test_foo_multi[1-val]',
                                            'test_foo_multi[B]']
