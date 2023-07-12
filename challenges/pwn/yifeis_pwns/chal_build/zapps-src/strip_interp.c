#include <elf.h>
#include <errno.h>
#include <error.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

#define PT_ZAPPS_INTERP 0xa26d1ecc

int main(int argc, char **argv)
{
    if (argc != 2)
        error(1, 0, "Usage: %s [filename]", argv[0]);

    int fd = open(argv[1], O_RDWR);
    if (fd < 0)
        error(1, errno, "%s", argv[1]);

    Elf64_Ehdr ehdr;
    if (read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr))
        error(1, errno, "read ehdr");

    for (int i = 0; i < ehdr.e_phnum; i++) {
        Elf64_Phdr phdr;

        if (pread(fd, &phdr, sizeof(phdr), ehdr.e_phoff + i * sizeof(phdr)) != sizeof(phdr))
            error(1, errno, "read phdr");

        if (phdr.p_type != PT_INTERP)
            continue;

        phdr.p_type = PT_ZAPPS_INTERP;
        if (pwrite(fd, &phdr, sizeof(phdr), ehdr.e_phoff + i * sizeof(phdr)) != sizeof(phdr))
            error(1, errno, "write phdr");
    }
}
