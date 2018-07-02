
A small tool to help trigger snippet expansion of ncm2 completion item based
on [snipMate](https://github.com/msanders/snipmate.vim).

vimrc config:

```vim
" press enter key to trigger snippet expansion
imap <expr> <CR> ncm2_snipmate#expand_or("\<CR>")
```
