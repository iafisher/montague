Static analysis of English text: verify the internal consistency of a piece of English text.

Other cool applications:

- Generate Unix commands from English text, e.g.

```shell
$ Remove the file extension from all the files in this directory
for path in ./*; do
  mv "$path" "${path%.*}"
done
```

