# encoding: utf-8
#
# Copyright (C) 2016 YouCompleteMe contributors
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *  # noqa
from future.utils import PY2

from mock import patch, call
from nose.tools import eq_
from hamcrest import contains_string

from ycm.test_utils import MockVimModule, ExtendedMock
MockVimModule()

from ycm.omni_completer import OmniCompleter
from ycm.test_utils import ExpectedFailure
from ycm.tests.server_test import MakeUserOptions, Server_test

from ycmd.utils import ToBytes
from ycmd.request_wrap import RequestWrap


def ToBytesOnPY2( data ):
  # To test the omnifunc, etc. returning strings, which can be of different
  # types depending on python version, we use ToBytes on PY2 and just the native
  # str on python3. This roughly matches what happens between py2 and py3
  # versions within Vim
  if PY2:
    return ToBytes( data )

  return data


def BuildRequest( line_num, column_num, contents ):
  # Note: it would be nice to use ycmd.test_utils.BuildRequest directly here,
  # but we can't import ycmd.test_utils because that in turn imports ycm_core,
  # which would cause our "ycm_core not imported" test to fail.
  return {
    'line_num': line_num,
    'column_num': column_num,
    'filepath': '/test',
    'file_data': {
      '/test': {
        'contents': contents,
        'filetypes': [ 'java' ] # We need a filetype with a trigger, so we just
                                # use java
      }
    }
  }


def BuildRequestWrap( line_num, column_num, contents ):
  return RequestWrap( BuildRequest( line_num, column_num, contents ) )


class OmniCompleter_test( Server_test ):

  def OmniCompleter_GetCompletions_Cache_List_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = 'test.'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 6,
                                     contents = contents )


    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( 'a' ),
                        ToBytesOnPY2( 'b' ),
                        ToBytesOnPY2( 'cdef' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'')" ),
      ] )

      eq_( results, omnifunc_result )


  def OmniCompleter_GetCompletions_Cache_ListFilter_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = 'test.t'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 7,
                                     contents = contents )

    eq_( request_data[ 'query' ], 't' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( 'a' ),
                        ToBytesOnPY2( 'b' ),
                        ToBytesOnPY2( 'cdef' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'t')" ),
      ] )

      eq_( results, [] )


  def OmniCompleter_GetCompletions_NoCache_List_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 0
    } ) )

    contents = 'test.'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 6,
                                     contents = contents )


    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( 'a' ),
                        ToBytesOnPY2( 'b' ),
                        ToBytesOnPY2( 'cdef' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'')" ),
      ] )

      eq_( results, omnifunc_result )


  def OmniCompleter_GetCompletions_NoCache_ListFilter_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 0
    } ) )

    contents = 'test.t'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 7,
                                     contents = contents )

    eq_( request_data[ 'query' ], 't' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( 'a' ),
                        ToBytesOnPY2( 'b' ),
                        ToBytesOnPY2( 'cdef' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'t')" ),
      ] )

      # actual result is that the results are not filtered, as we expect the
      # omniufunc or vim itself to do this filtering
      eq_( results, omnifunc_result )


  @ExpectedFailure( 'We ignore the result of the call to findstart and use our '
                    'own interpretation of where the identifier should be',
                    contains_string( "test_omnifunc(0,'t')" ) )
  def OmniCompleter_GetCompletsions_UseFindStart_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = 'test.t'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 7,
                                     contents = contents )

    eq_( request_data[ 'query' ], 't' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( 'a' ),
                        ToBytesOnPY2( 'b' ),
                        ToBytesOnPY2( 'cdef' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 1, omnifunc_result ] ) as vim_eval:
      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),

        # Fails here: actual result is that the findstart result (1) is ignored
        # and we use the 't' query as we normally would on the server side
        call( "test_omnifunc(0,'test.t')" ),
      ] )

      eq_( results, omnifunc_result )


  def OmniCompleter_GetCompletions_Cache_Object_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = 'test.t'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 7,
                                     contents = contents )

    eq_( request_data[ 'query' ], 't' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = {
      'words': [
        ToBytesOnPY2( 'a' ),
        ToBytesOnPY2( 'b' ),
        ToBytesOnPY2( 'CDtEF' )
      ]
    }

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'t')" ),
      ] )

      eq_( results, [ ToBytesOnPY2( 'CDtEF' ) ] )


  def OmniCompleter_GetCompletions_Cache_ObjectList_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = 'test.tt'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 8,
                                     contents = contents )

    eq_( request_data[ 'query' ], 'tt' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [
      {
        'word': ToBytesOnPY2( 'a' ),
        'abbr': ToBytesOnPY2( 'ABBR'),
        'menu': ToBytesOnPY2( 'MENU' ),
        'info': ToBytesOnPY2( 'INFO' ),
        'kind': ToBytesOnPY2( 'K' )
      },
      {
        'word': ToBytesOnPY2( 'test' ),
        'abbr': ToBytesOnPY2( 'ABBRTEST'),
        'menu': ToBytesOnPY2( 'MENUTEST' ),
        'info': ToBytesOnPY2( 'INFOTEST' ),
        'kind': ToBytesOnPY2( 'T' )
      }
    ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'tt')" ),
      ] )

      eq_( results, [ omnifunc_result[ 1 ] ] )


  def OmniCompleter_GetCompletions_NoCache_ObjectList_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 0
    } ) )

    contents = 'test.tt'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 8,
                                     contents = contents )

    eq_( request_data[ 'query' ], 'tt' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [
      {
        'word': ToBytesOnPY2( 'a' ),
        'abbr': ToBytesOnPY2( 'ABBR'),
        'menu': ToBytesOnPY2( 'MENU' ),
        'info': ToBytesOnPY2( 'INFO' ),
        'kind': ToBytesOnPY2( 'K' )
      },
      {
        'word': ToBytesOnPY2( 'test' ),
        'abbr': ToBytesOnPY2( 'ABBRTEST'),
        'menu': ToBytesOnPY2( 'MENUTEST' ),
        'info': ToBytesOnPY2( 'INFOTEST' ),
        'kind': ToBytesOnPY2( 'T' )
      }
    ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'tt')" ),
      ] )

      # We don't filter the result - we expect the omnifunc to do that
      # based on the query we supplied (Note: that means no fuzzy matching!)
      eq_( results, omnifunc_result )


  def OmniCompleter_GetCompletions_Cache_ObjectListObject_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = 'test.tt'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 8,
                                     contents = contents )

    eq_( request_data[ 'query' ], 'tt' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = {
      'words': [
        {
          'word': ToBytesOnPY2( 'a' ),
          'abbr': ToBytesOnPY2( 'ABBR'),
          'menu': ToBytesOnPY2( 'MENU' ),
          'info': ToBytesOnPY2( 'INFO' ),
          'kind': ToBytesOnPY2( 'K' )
        },
        {
          'word': ToBytesOnPY2( 'test' ),
          'abbr': ToBytesOnPY2( 'ABBRTEST'),
          'menu': ToBytesOnPY2( 'MENUTEST' ),
          'info': ToBytesOnPY2( 'INFOTEST' ),
          'kind': ToBytesOnPY2( 'T' )
        }
      ]
    }

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'tt')" ),
      ] )

      eq_( results, [ omnifunc_result[ 'words' ][ 1 ] ] )


  def OmniCompleter_GetCompletions_NoCache_ObjectListObject_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 0
    } ) )

    contents = 'test.tt'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 8,
                                     contents = contents )

    eq_( request_data[ 'query' ], 'tt' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = {
      'words': [
        {
          'word': ToBytesOnPY2( 'a' ),
          'abbr': ToBytesOnPY2( 'ABBR'),
          'menu': ToBytesOnPY2( 'MENU' ),
          'info': ToBytesOnPY2( 'INFO' ),
          'kind': ToBytesOnPY2( 'K' )
        },
        {
          'word': ToBytesOnPY2( 'test' ),
          'abbr': ToBytesOnPY2( 'ABBRTEST'),
          'menu': ToBytesOnPY2( 'MENUTEST' ),
          'info': ToBytesOnPY2( 'INFOTEST' ),
          'kind': ToBytesOnPY2( 'T' )
        }
      ]
    }

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'tt')" ),
      ] )

      # No FilterAndSortCandidates for cache_omnifunc=0 (we expect the omnifunc
      # to do the filtering?)
      eq_( results, omnifunc_result[ 'words' ] )


  def OmniCompleter_GetCompletions_Cache_List_Unicode_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = '?????sty_??.'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 13,
                                     contents = contents )


    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( '???est' ),
                        ToBytesOnPY2( '??_unicode_identifier' ),
                        ToBytesOnPY2( '?????????????? yummy ??ie' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'')" ),
      ] )

      eq_( results, omnifunc_result )


  def OmniCompleter_GetCompletions_NoCache_List_Unicode_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 0
    } ) )

    contents = '?????sty_??.'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 13,
                                     contents = contents )


    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( '???est' ),
                        ToBytesOnPY2( '??_unicode_identifier' ),
                        ToBytesOnPY2( '?????????????? yummy ??ie' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'')" ),
      ] )

      eq_( results, omnifunc_result )


  @ExpectedFailure( 'Filtering on unicode is not supported by the server' )
  def OmniCompleter_GetCompletions_Cache_List_Filter_Unicode_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = '?????sty_??.????'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 17,
                                     contents = contents )


    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( '???est' ),
                        ToBytesOnPY2( '??_unicode_identifier' ),
                        ToBytesOnPY2( '?????????????? yummy ??ie' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'????')" ),
      ] )

      # Fails here: Filtering on unicode is not supported
      eq_( results, [ omnifunc_result[ 2 ] ] )


  def OmniCompleter_GetCompletions_NoCache_List_Filter_Unicode_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 0
    } ) )

    contents = '?????sty_??.????'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 17,
                                     contents = contents )


    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [ ToBytesOnPY2( '?????????????? yummy ??ie' ) ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )
      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'????')" ),
      ] )

      eq_( results, omnifunc_result )


  @ExpectedFailure( 'Filtering on unicode is not supported by the server' )
  def OmniCompleter_GetCompletions_Cache_ObjectList_Unicode_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = '?????sty_??.????'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 17,
                                     contents = contents )


    eq_( request_data[ 'query' ], '????' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = [
      {
        'word': ToBytesOnPY2( '??lpha???et' ),
        'abbr': ToBytesOnPY2( '??????????'),
        'menu': ToBytesOnPY2( '????~????' ),
        'info': ToBytesOnPY2( '^~fo' ),
        'kind': ToBytesOnPY2( '??' )
      },
      {
        'word': ToBytesOnPY2( '??????????????' ),
        'abbr': ToBytesOnPY2( '?????????????????'),
        'menu': ToBytesOnPY2( '??????????????????' ),
        'info': ToBytesOnPY2( '?????????????????' ),
        'kind': ToBytesOnPY2( '??' )
      }
    ]

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'????')" ),
      ] )

      # Fails here: Filtering on unicode is not supported
      eq_( results, [ omnifunc_result[ 1 ] ] )


  def OmniCompleter_GetCompletions_Cache_ObjectListObject_Unicode_test( self ):
    omni_completer = OmniCompleter( MakeUserOptions( {
      'cache_omnifunc': 1
    } ) )

    contents = '?????sty_??.t'
    request_data = BuildRequestWrap( line_num = 1,
                                     column_num = 14,
                                     contents = contents )


    eq_( request_data[ 'query' ], 't' )

    # Make sure there is an omnifunc set up.
    with patch( 'vim.eval', return_value = ToBytesOnPY2( 'test_omnifunc' ) ):
      omni_completer.OnFileReadyToParse( request_data )

    omnifunc_result = {
      'words': [
        {
          'word': ToBytesOnPY2( '??lpha???et' ),
          'abbr': ToBytesOnPY2( '??????????'),
          'menu': ToBytesOnPY2( '????~????' ),
          'info': ToBytesOnPY2( '^~fo' ),
          'kind': ToBytesOnPY2( '??' )
        },
        {
          'word': ToBytesOnPY2( '??????????????' ),
          'abbr': ToBytesOnPY2( '?????????????????'),
          'menu': ToBytesOnPY2( '??????????????????' ),
          'info': ToBytesOnPY2( '?????????????????' ),
          'kind': ToBytesOnPY2( '??' )
        },
        {
          'word': ToBytesOnPY2( 'test' ),
          'abbr': ToBytesOnPY2( '?????????????????'),
          'menu': ToBytesOnPY2( '??????????????????' ),
          'info': ToBytesOnPY2( '?????????????????' ),
          'kind': ToBytesOnPY2( '??' )
        }
      ]
    }

    # And get the completions
    with patch( 'vim.eval',
                new_callable = ExtendedMock,
                side_effect = [ 6, omnifunc_result ] ) as vim_eval:

      results = omni_completer.ComputeCandidates( request_data )

      vim_eval.assert_has_exact_calls( [
        call( 'test_omnifunc(1,"")' ),
        call( "test_omnifunc(0,'t')" ),
      ] )

      # Note: the filtered results are all unicode objects (not bytes) because
      # they are passed through the FilterAndSortCandidates machinery
      # (via the server)
      eq_( results, [ {
        'word': 'test',
        'abbr': '?????????????????',
        'menu': '??????????????????',
        'info': '?????????????????',
        'kind': '??'
      } ] )
