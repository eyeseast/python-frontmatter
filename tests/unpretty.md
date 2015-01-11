---
destination:
  encoding:
    xz:
      enabled: true
      min_size: 5120
      options:
      path_filter:
  result:
    append_to_file:
    append_to_lafs_dir:
    print_to_stdout: true
  url: http://localhost:3456/uri
filter:
  - 'Длинный стринг на русском'
  - 'Еще одна длинная строка'
---

This is a test of both unicode and prettier dumping. The above metadata comes from the [pretty-yaml](https://github.com/mk-fg/pretty-yaml) readme file.

Metadata should be dumped in order.