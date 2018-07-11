[UltiSnips](https://github.com/SirVer/ultisnips) integration for
[ncm2](https://github.com/ncm2/ncm2).

![rec](https://user-images.githubusercontent.com/4538941/42503042-2b7da088-846a-11e8-837d-17432a444d97.gif)

## Features

- snippet completion source
- trigger dynamic snippet of completed item, e.g. parameter expansion.

## Reaurements

- `user_data` found in vim8/nvim's documentation `:help complete-item`

## Install

```vim
" based on ultisnips
Plug 'ncm2/ncm2-ultisnips'
Plug 'SirVer/ultisnips'
```

## Vimrc Example

```vim
" Press enter key to trigger snippet expansion
" The parameters are the same as `:help feedkeys()`
inoremap <silent> <expr> <CR> ncm2_ultisnips#expand_or("\<CR>", 'n')

" c-j c-k for moving in snippet
" let g:UltiSnipsExpandTrigger		= "<Plug>(ultisnips_expand)"
let g:UltiSnipsJumpForwardTrigger	= "<c-j>"
let g:UltiSnipsJumpBackwardTrigger	= "<c-k>"
let g:UltiSnipsRemoveSelectModeMappings = 0
```

`:help UltiSnips` for more information on using UltiSnips.

## API

If you need more control over the completed item's snippet expansion, you
might need these two APIs to help program your key mapping.

`ncm2_ultisnips#completed_is_snippet()`

Checks whether the `v:completed_item` is also a snippet.

`<Plug>(ncm2_ultisnips_expand_completed)`

Use this key to expand the completed snippet.
