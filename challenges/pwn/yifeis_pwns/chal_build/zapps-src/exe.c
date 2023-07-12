#include <errno.h>
#include <error.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

extern void foo(void);

static __attribute__((constructor)) void static_constructor(void) {
    printf("static_constructor in exe invoked\n");
}

int main(int argc, char **argv)
{
    printf("main invoked with arguments:\n");
    for (int i = 0; i < argc; i++) {
        printf("argv[%d] = %s\n", i, argv[i]);
    }

    foo();

    int fd = open("/proc/self/maps", O_RDONLY | O_CLOEXEC);
    if (fd < 0)
        error(1, errno, "/proc/self/maps");

    printf("contents of /proc/self/maps:\n");
    for (;;) {
        char buf[128];
        int len = read(fd, buf, sizeof(buf));
        if (len <= 0)
            break;
        (void)!write(STDOUT_FILENO, buf, len);
    }
}
