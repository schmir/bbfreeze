// run frozen programs

#include <Python.h>

#ifdef WIN32
#include <windows.h>
#endif

#include <compile.h>
#include <eval.h>

#include <limits.h>
#include <stdio.h>

#ifdef HAVE_SYS_PARAM_H
#include <sys/param.h>
#endif

#ifdef HAVE_STDLIB_H
#include <stdlib.h>
#endif

static int exists(const char *name)
{
	FILE *f=fopen(name, "rb");
	if (f) {
		fclose(f);
		return 1;
	}
	return 0;
}

static void FatalError(const char *message)
{
	PyErr_Print();
#ifdef GUI
	MessageBox(NULL, message, "bbfreeze Fatal Error", MB_ICONERROR);
	exit(1);
#endif

	Py_FatalError(message);
}

static void dirname(const char *path)
{
#ifdef WIN32
	int sep='\\';
#else
	int sep='/';
#endif
	char *lastsep = strrchr(path, sep);
	if (lastsep==0) {
		FatalError("dirname failed.");
	}
	*lastsep = 0;
}

static void addToPath(const char *p)
{
	PyObject *pathList, *temp;
	
	pathList = PySys_GetObject("path");
	if (!pathList) {
		FatalError("cannot acquire sys.path");
	}

	temp = PyString_FromString(p);
	if (!temp) {
		FatalError("cannot create Python string");
	}

	if (PyList_Insert(pathList, 0, temp) < 0) {
		FatalError("cannot insert file name in sys.path");
	}
	
	Py_DECREF(temp);
}

static int ExecuteScript(const char *fileName)		// name of file containing Python code
{
	PyObject *locals;
	PyObject *tmp;
	const char *resolved_path = fileName;
	char *tmppath;

#ifdef HAVE_REALPATH
	static char buffer[PATH_MAX+1];

	if (realpath(fileName, buffer)) {
		resolved_path = buffer;
	}
#endif

	tmppath = (char*)malloc(strlen(resolved_path)+64);
	if (!tmppath) {
		FatalError("malloc failed");
	}
	strcpy(tmppath, resolved_path);
	dirname(tmppath);
	addToPath(tmppath);

#ifdef WIN32
	strcat(tmppath, "\\library.zip");
#else
	strcat(tmppath, "/library.zip");
#endif

	if (exists(tmppath)) {
		addToPath(tmppath);
	} else {
		addToPath(resolved_path);
	}
	free(tmppath);

	// sys.path isn't as empty as one might hope. when using zipfile compression
	// the zlib module must be loaded. without cleaning sys.path here, it did happen 
	// that trying to run a frozen executable sometimes did, and sometimes did not find 
	// zlib depending on the way you called the frozen executable (i.e. 'dist/foobar'
	// vs 'foobar'). When cleaning sys.path with the following code, it will always 
	// fail :)
	
	
	locals = PyDict_New();
	if (!locals) {
		FatalError("PyDict_New failed.");
	}

	PyDict_SetItemString(locals, "__builtins__", PyEval_GetBuiltins());

	tmp = PyRun_String(
		"import sys\n"
		"del sys.path[2:]\n"
		"sys.frozen=1\n"
		"import zipimport\n"
		"importer = zipimport.zipimporter(sys.path[0])\n"
		"import __builtin__\n"
		"m = __builtin__.__import__('__main__')\n"
		"exec importer.get_code('__main__')\n",
		Py_file_input, locals, 0
		);

	Py_DECREF(locals);

	if (!tmp) {
		PyErr_Print();
	}

	Py_Finalize();
	return tmp ? 0 : 1;
}

static void set_program_path(char *argv0)
{
#ifndef WIN32
	char progpath[PATH_MAX+1];
	int count;

	count=readlink("/proc/self/exe", progpath, PATH_MAX);
	if (count < 0) {
		count = readlink("/proc/curproc/file", progpath, PATH_MAX);
	}
	if (count < 0) {
		Py_SetProgramName(argv0);
	} else {
		progpath[count] = 0;
		Py_SetProgramName(progpath);
	}
#else
	Py_SetProgramName(argv0);
#endif
}

static int loader_main(int argc, char **argv)
{
	const char *fileName;
	// initialize Python
	Py_NoSiteFlag = 1;
	Py_FrozenFlag = 1;
	Py_IgnoreEnvironmentFlag = 1;
	Py_SetPythonHome("");

	set_program_path(argv[0]);

	fileName = Py_GetProgramFullPath();
	Py_Initialize();

	PySys_SetArgv(argc, argv);

	return ExecuteScript(fileName);
}
