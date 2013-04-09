#include "loader_impl.h"

int WINAPI
WinMain(HINSTANCE hInst, HINSTANCE hPrevInst, LPSTR lpCmdLine, int nCmdShow)
{
	return loader_main(__argc, __argv);
}
