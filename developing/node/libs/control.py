import Pyro4
import utils
import time
import token
import threading
from termcolor import colored

# decoradores para las clases generales


def load_config(in_function):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control """
    def out_function(*args, **kwargs):
        _self = args[0]
        try:
            _self.DATA = args[1]
        except Exception:
            pass
        _self.__dict__.update(kwargs)
        super(_self.__class__.__mro__[0], _self).__init__()
        in_function(*args, **kwargs)
    return out_function


def Pyro4bot_Loader(cls, kwargs):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control
    """
    original_init = cls.__init__

    def init(self):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super(cls, self).__init__()
        original_init(self)
    cls.__init__ = init
    return cls


def load_node(in_function):
    """this Decorator load all parameter defined in Json configuration in node object """
    def out_function(*args, **kwargs):

        _self = args[0]
        _self.__dict__.update(kwargs)
        in_function(*args, **kwargs)
    return out_function


def flask(*args_decorator):
    def flask_decorator(func):
        original_doc = func.__doc__
        if func.__doc__ is None:
            original_doc = ""
        if len(args_decorator) % 2 == 0:  # Tuplas
            for i in xrange(0, len(args_decorator), 2):
                original_doc += "\n\t@type:" + \
                    args_decorator[i] + "\n\t@count:" + \
                    str(args_decorator[i + 1])
        elif len(args_decorator) == 1:
            original_doc += "\n\t@type:" + \
                args_decorator[0] + "\n\t@count:" + \
                str(func.__code__.co_argcount - 1)
        func.__doc__ = original_doc
        print original_doc
        def func_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func_wrapper.__doc__ = original_doc
        return func_wrapper
    return flask_decorator


class Control(object):
    """ This class provide threading funcionality to all object in node.
        Init workers Threads and PUB/SUB thread"""

    def __init__(self):
        self.mutex = threading.Lock()
        self.workers = []

    def init_workers(self, fn):
        """ Start all workers daemon"""
        if type(fn) not in (list, tuple):
            fn = (fn,)
        if self.worker_run:
            for func in fn:
                t = threading.Thread(target=func, args=())
                self.workers.append(t)
                t.setDaemon(True)
                t.start()

    def init_thread(self, fn, *args):
        """ Start all workers daemon"""
        if self.worker_runa:
            t = threading.Thread(target=fn, args=args)
            self.workers.append(t)
            t.setDaemon(True)
            t.start()

    def init_publisher(self, token_data, frec=0.01):
        """ Start publisher daemon"""
        self.threadpublisher = False
        self.token_data = None
        self.subscriptors = {}
        if isinstance(token_data, token.Token):
            self.threadpublisher = True
            t = threading.Thread(target=self.thread_publisher,
                                 args=(token_data, frec))
            self.workers.append(t)
            t.setDaemon(True)
            t.start()
        else:
            print(
                "ERROR: Can not publish to object other than token {}".format(token_data))

    def thread_publisher(self, token_data, frec):
        """ public data between all subcriptors in list"""
        while self.threadpublisher:
            d = token_data.get_attribs()
            try:
                for key in self.subscriptors.keys():
                    subscriptors = self.subscriptors[key]
                    try:
                        if key in d:
                            for item in subscriptors:
                                # print("publicando",key, d[key])
                                item.publication(key, d[key])
                    except TypeError:
                        print "Argumento no esperado."
                        raise
                        exit()
            except Exception as e:
                print utils.format_exception(e)
                raise
            time.sleep(frec)

    @Pyro4.expose
    def send_subscripcion(self, obj, key):
        """ Send a subcripcion request to an object"""
        try:
            obj.subscribe(key, self.pyro4id)
        except Exception:
            print("ERROR: in subscripcion %s URI: %s" % (obj, key))
            raise
            return False

    @Pyro4.expose
    def subscribe(self, key, uri):
        """ Receive a request for subcripcion from an object and save data in dict subcriptors
            Data estructure store one item subcripcion (key) and subcriptors proxy list """
        try:
            if key not in self.subscriptors:
                self.subscriptors[key] = []
            proxy = self.__dict__["uriresolver"].get_proxy(uri)
            self.subscriptors[key].append(proxy)
            return True
        except Exception:
            print("ERROR: in subscribe")
            raise
            return False

    @Pyro4.oneway
    @Pyro4.expose
    def publication(self, key, value):
        """ Is used to public in this object a item value """
        try:
            # print("setattr",key,value)
            setattr(self, key, value)
        except Exception:
            raise

    def adquire(self):
        self.mutex.adquire()

    def release(self):
        self.mutex.release()

    def stop(self):
        self.worker_run = False

    @Pyro4.expose
    def echo(self, msg="hello"):
        return msg

    @Pyro4.expose
    def get_pyroid(self):
        return self.pyro4id

    @Pyro4.expose
    def __exposed__(self):
        return self.exposed

    @Pyro4.expose
    def __docstring__(self):
        return self.docstring

    @Pyro4.expose
    def get_class(self):
        return self._dict__[cls]

    @Pyro4.expose
    @Pyro4.callback
    def add_resolved_remote_dep(self, dep):
        if isinstance(dep, dict):
            print(colored("New remote dep! {}".format(dep), "green"))
            k = dep.keys()[0]
            try:
                for u in dep[k]:
                    self.deps[k] = utils.get_pyro4proxy(u, k.split(".")[0])
                self._resolved_remote_deps.append(dep[k])
                if (self._unr_remote_deps is not None):
                    if k in self._unr_remote_deps:
                        self._unr_remote_deps.remove(k)
            except Exception:
                pass
            self.check_remote_deps()

    def check_remote_deps(self):
        status = True
        if (self._unr_remote_deps is not None and self._unr_remote_deps):
            for unr in self._unr_remote_deps:
                if "*" not in unr:
                    status = False
        for k in self.deps.keys():
            try:
                if (self.deps[k].echo() != "hello"):
                    status = False
            except Exception:
                status = False

        if (status):
            self._REMOTE_STATUS = "OK"
        return self._REMOTE_STATUS
