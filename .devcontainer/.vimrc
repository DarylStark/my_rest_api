"---------------------------------------------------------------------------------------------------
" Functions
"---------------------------------------------------------------------------------------------------
function! ToggleRelativeNumber()
    " Function to toggle relative numbers
    if(&relativenumber == 1)
        set norelativenumber
    else
        set relativenumber
    endif
endfunc
"---------------------------------------------------------------------------------------------------
function! ToggleHLSearch()
    " Function to toggle HL search
    if(&hlsearch == 1)
        set nohlsearch
    else
        set hlsearch
    endif
endfunc
"---------------------------------------------------------------------------------------------------
function! GetMode()
    " Function that returns the current mode as a string. Usefull in the
    " statusline for example
    if(mode() == 'n')
        return 'NORMAL'
    elseif(mode() == 'i')
        return 'INSERT'
    elseif(mode() == 'R')
        return 'REAPLCE'
    elseif(mode() == 'v' || mode() == 'V')
        return 'VISUAL'
    else
        return 'Unknown: ' . mode()
    endif
endfunc
"---------------------------------------------------------------------------------------------------
" Syntax Highlighting
"---------------------------------------------------------------------------------------------------
syntax on
colorscheme elflord
"---------------------------------------------------------------------------------------------------
" Indentation
"---------------------------------------------------------------------------------------------------
set autoindent
filetype plugin indent on
set tabstop=4
set expandtab
set shiftwidth=4
set softtabstop=4
"---------------------------------------------------------------------------------------------------
" Line numbering
"---------------------------------------------------------------------------------------------------
set number
set relativenumber
"---------------------------------------------------------------------------------------------------
" Search settings
"---------------------------------------------------------------------------------------------------
set hlsearch                " Enables search highlighting
set incsearch               " Enables search highlighting while typing
"---------------------------------------------------------------------------------------------------
" Tabline and statusbar settings
"---------------------------------------------------------------------------------------------------
set showtabline=2           " Always show the tabbar on the top
set laststatus=2            " Always show the status line on the bottom
"---------------------------------------------------------------------------------------------------
" Configure the statusbar
"---------------------------------------------------------------------------------------------------
set statusline=
set statusline+=%{GetMode()}
set statusline+=%3n\ 
set statusline+=%r
set statusline+=%f\ %m
set statusline+=%=
set statusline+=%l,%c
set statusline+=\ (%p%%)\ 
"---------------------------------------------------------------------------------------------------
" Folding settings
"---------------------------------------------------------------------------------------------------
set foldenable              " Enable folding
set foldlevelstart=10       " Only fold from level 10
set foldmethod=indent       " Fold on indentation
"---------------------------------------------------------------------------------------------------
" Custom Commands for Git
"---------------------------------------------------------------------------------------------------
command! GitStatus                  :!git status
command! GitAddFile                 :!git add %
command! GitAddAll                  :!git add --all
command! GitCommit                  :!git commit
command! GitStash                   :!git stash
command! GitLogOneline              :!git log --oneline --graph
command! GitDiff                    :!git diff %
"---------------------------------------------------------------------------------------------------
" Custom Commands for Python
"---------------------------------------------------------------------------------------------------
autocmd FileType python command! PythonRunFile              :!python3 %
autocmd FileType python command! PythonRunFileInteractive   :!python3 -i %
command! PythonShell                :!python3
"---------------------------------------------------------------------------------------------------
" Custom Commands for C++
"---------------------------------------------------------------------------------------------------
autocmd FileType cpp command! CPPCompileAndRun               :!g++ -std=c++17 % -o ../bin/tests && ../bin/tests
"---------------------------------------------------------------------------------------------------
" Other configuration
"---------------------------------------------------------------------------------------------------
set autoread
set showcmd                         " Show the running command on the bottom
set updatetime=100                  " Change the writing of the swap file to 100ms
"---------------------------------------------------------------------------------------------------
" Configuration for Plugin: GitGutter
"---------------------------------------------------------------------------------------------------
let g:gitgutter_map_keys = 0        " Disable automatic keybindings for GitGutter
"---------------------------------------------------------------------------------------------------
" Keymappings for NORMAL mode
"---------------------------------------------------------------------------------------------------
" Configuration for keymappings
let mapleader = ';'

" Keymappings for folding
nnoremap <space>                  za

" Keymappings to toogle relative line numbers and HL search
nnoremap <silent> %                 :call ToggleRelativeNumber()<CR>
nnoremap <silent> <leader><leader>  :call ToggleHLSearch()<CR>

" Keymappings to go to a previous tab
nnoremap <silent> <Tab>             :tabnext<CR>
nnoremap <silent> <S-Tab>           :tabprev<CR>

" Keymappings to run Python files 
autocmd FileType python nnoremap <silent> <leader>p :PythonRunFile<CR>
autocmd FileType python nnoremap <silent> <leader>P :PythonRunFileInteractive<CR>

" Keymappings to compile and run C++ files
autocmd FileType cpp nnoremap <silent> <leader>p :CPPCompileAndRun<CR>

" Keymappings to start appliactions
nnoremap <silent> ,p                :PythonShell<CR>
nnoremap <silent> ,s                :shell<CR>

" Keymappings for Git
nnoremap <silent> <leader>gs        :GitStatus<CR>
nnoremap <silent> <leader>ga        :GitAddFile<CR>
nnoremap <silent> <leader>gA        :GitAddAll<CR>
nnoremap <silent> <leader>gc        :GitCommit<CR>
nnoremap <silent> <leader>gS        :GitStash<CR>
nnoremap <silent> <leader>gl        :GitLogOneline<CR>
nnoremap <silent> <leader>gd        :GitDiff<CR>

nmap )                              0
nmap 0                              ^

" Keymappings for buffer changing
nmap <silent> {{                    :bp<CR>
nmap <silent> }}                    :bn<CR>
nmap <silent> <leader>l             :ls<CR>
nmap <silent> <leader>c             :Bclose<CR>

" Keymappings for GitGutter
nmap <silent> <leader>gt            :GitGutterLineHighlightsToggle<CR>
nmap <silent> <leader>gn            <Plug>(GitGutterNextHunk)
nmap <silent> <leader>gp            <Plug>(GitGutterPrevHunk)
"---------------------------------------------------------------------------------------------------
" Keymappings for INSERT mode
"---------------------------------------------------------------------------------------------------
" Keymappings to insert a hashbang automatically based on filetype
autocmd FileType python inoremap <C-b>  #!/usr/bin/env python3<CR>
autocmd FileType sh     inoremap <C-b>  #!/bin/bash<CR>

" Keymappings to insert the date and time
inoremap <C-d> <C-r>=system('date +\%Y-\%M-\%d \| tr -d "\n"')<CR>
inoremap <C-n> <C-r>=system('date +\%H:\%m:\%S \| tr -d "\n"')<CR>
"---------------------------------------------------------------------------------------------------
" Keymappings for VISUAL mode
"---------------------------------------------------------------------------------------------------
" External filters
vnoremap <silent> <C-r>             !rev<CR>
"---------------------------------------------------------------------------------------------------
