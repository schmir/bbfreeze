// run frozen programs

#include <Python.h>
#include <osdefs.h>

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

/* what follows is a copy of sysmodule.c's PySys_SetPath
 * we use this to change the sys.path according to our needs
 * (PySys_SetPath is called from Py_Initialize)
 */

static char *syspath = 0;

#ifndef WIN32
static PyObject *
makepathobject(char *path, int delim)
{
	int i, n;
	char *p;
	PyObject *v, *w;

	n = 1;
	p = path;
	while ((p = strchr(p, delim)) != NULL) {
		n++;
		p++;
	}
	v = PyList_New(n);
	if (v == NULL)
		return NULL;
	for (i = 0; ; i++) {
		p = strchr(path, delim);
		if (p == NULL)
			p = strchr(path, '\0'); /* End of string */
		w = PyString_FromStringAndSize(path, (Py_ssize_t) (p - path));
		if (w == NULL) {
			Py_DECREF(v);
			return NULL;
		}
		PyList_SetItem(v, i, w);
		if (*p == '\0')
			break;
		path = p+1;
	}
	return v;
}

static void
PySys_SetPath_orig(char *path)
{
	PyObject *v;
	if ((v = makepathobject(path, DELIM)) == NULL)
		Py_FatalError("can't create sys.path");
	if (PySys_SetObject("path", v) != 0)
		Py_FatalError("can't assign sys.path");
	Py_DECREF(v);
}

void
PySys_SetPath(char *path)
{
	if (syspath) {
		PySys_SetPath_orig(syspath);
	} else {
		PySys_SetPath_orig(path);
	}
}
#endif

static void fatal(const char *message)
{
#ifdef GUI
	MessageBox(NULL, message, "bbfreeze Fatal Error", MB_ICONERROR);
#else
	fprintf(stderr, "Fatal error: %s", message);	
#endif
	exit(1);
}

static void dirname(const char *path)
{
	char *lastsep = strrchr(path, SEP);
	if (lastsep==0) {
		fatal("dirname failed.");
	}
	*lastsep = 0;
}

static void compute_syspath()
{
	const char *resolved_path = strdup(Py_GetProgramFullPath());

#ifdef HAVE_REALPATH
	static char buffer[PATH_MAX+1];

	if (realpath(resolved_path, buffer)) {
		resolved_path = buffer;
	}
#endif

	dirname(resolved_path);
	syspath = malloc(2*strlen(resolved_path)+64);

	sprintf(syspath, "%s%clibrary.zip%c%s", resolved_path, SEP, DELIM, resolved_path);
	fprintf(stderr, "syspath: %s\n", syspath);
}

static int run_script()
{
	PyObject *locals;
	PyObject *tmp;

	// sys.path isn't as empty as one might hope. when using zipfile compression
	// the zlib module must be loaded. without cleaning sys.path here, it did happen 
	// that trying to run a frozen executable sometimes did, and sometimes did not find 
	// zlib depending on the way you called the frozen executable (i.e. 'dist/foobar'
	// vs 'foobar'). When cleaning sys.path with the following code, it will always 
	// fail :)
	
	
	locals = PyDict_New();
	if (!locals) {
		fatal("PyDict_New failed.");
	}

	PyDict_SetItemString(locals, "__builtins__", PyEval_GetBuiltins());

	tmp = PyRun_String(
		"import sys\n"
		"del sys.path[2:]\n"
		"sys.frozen=1\n"
		"import zipimport\n"
		"importer = zipimport.zipimporter(sys.path[0])\n"
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
	// initialize Python
	Py_NoSiteFlag = 1;
	Py_FrozenFlag = 1;
	Py_IgnoreEnvironmentFlag = 1;
	Py_SetPythonHome("");

	set_program_path(argv[0]);

	compute_syspath();
	Py_Initialize();
	PySys_SetArgv(argc, argv);
	PySys_SetPath(syspath);
	free(syspath);
	syspath = 0;

	return run_script();
}
