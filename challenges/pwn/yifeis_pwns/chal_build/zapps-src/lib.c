#include <stdio.h>

static __attribute__((constructor)) void static_constructor(void) {
    printf("static_constructor in lib invoked\n");
}

void foo(void)
{
    printf("foo invoked\n");
}
