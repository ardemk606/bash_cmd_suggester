#include <sys/types.h>
#define _GNU_SOURCE 1          /* sigjmp_buf и др. */
#include "shell.h"
#include "builtins.h"

extern int suggester_cpp_builtin (WORD_LIST *);

static char *const hello_doc[] = {
    (char *)"bash builtin for ai-driven suggesting",
    (char *)"",
    (char *)"ctrl + e for suggestion",
    (char *)0
};

static char name[] = "suggester_cpp";

struct builtin hello_cpp_struct = {
    name,
    suggester_cpp_builtin,
    BUILTIN_ENABLED,
    hello_doc,
    (char *)"add next token to readline",
    0
};
