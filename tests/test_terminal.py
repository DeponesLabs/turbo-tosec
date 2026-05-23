import pytest
from unittest.mock import patch, MagicMock
from turbo_tosec.terminal import Console, UniversalProgress

class TestConsole:
    @patch('builtins.print')
    def test_info_output(self, mock_print):
        Console.info("System initializing")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "[*] System initializing" in args
        assert Console.OKBLUE in args

    @patch('builtins.print')
    def test_error_output(self, mock_print):
        Console.error("Critical failure")
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "[X] Critical failure" in args
        assert Console.FAIL in args

class TestUniversalProgress:
    @patch('turbo_tosec.terminal.tqdm.tqdm')
    def test_cli_mode_initializes_tqdm(self, mock_tqdm_class):
        with UniversalProgress(total=1000, desc="Testing") as pbar:
            assert pbar.console_bar is not None
            assert pbar.callback is None
            
            pbar.update(100)
            pbar.console_bar.update.assert_called_once_with(100)
            
            pbar.set_postfix({"ROMs": 5})
            pbar.console_bar.set_postfix.assert_called_once_with({"ROMs": 5})
            
        pbar.console_bar.close.assert_called_once()

    def test_gui_mode_uses_callback_bypasses_tqdm(self):
        mock_callback = MagicMock()
        
        with UniversalProgress(total=1000, callback=mock_callback) as pbar:
            assert pbar.console_bar is None
            assert pbar.callback is not None
            
            pbar.update(100)
            mock_callback.assert_called_once_with(100, 1000)
            
            # Should not raise any errors, just passes
            pbar.set_postfix({"ROMs": 5})
