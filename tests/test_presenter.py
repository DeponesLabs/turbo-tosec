import pytest
from unittest.mock import MagicMock, patch
from turbo_tosec.presenter import CLIPresenter

class TestCLIPresenter:

    @pytest.fixture
    def mock_pbar(self):
        
        pbar = MagicMock()
        pbar.console_bar = MagicMock()
        pbar.console_bar.total = 0
        return pbar

    @pytest.fixture
    def mock_session(self):
        
        session = MagicMock()
        session.total_roms = 1500
        session.error_count = 3
        return session

    def test_update_progress_syncs_bar_state(self, mock_pbar):
        
        presenter = CLIPresenter(pbar=mock_pbar)
        presenter.update_progress(500, 2000)
        
        assert mock_pbar.console_bar.total == 2000
        assert mock_pbar.current == 500
        assert mock_pbar.console_bar.n == 500
        mock_pbar.console_bar.refresh.assert_called_once()
        mock_pbar.set_postfix.assert_not_called()

    def test_update_progress_applies_session_postfix(self, mock_pbar, mock_session):
        
        presenter = CLIPresenter(pbar=mock_pbar, session=mock_session)
        presenter.update_progress(1000, 2000)
        mock_pbar.set_postfix.assert_called_once_with({"ROMs": 1500, "Errors": 3})

    @patch('turbo_tosec.presenter.tqdm')
    @patch('turbo_tosec.presenter.Console')
    def test_write_above_bar_delegates_to_tqdm(self, mock_console, mock_tqdm):
        
        mock_console.SYM_INFO = "[INFO]"
        CLIPresenter.write_above_bar("Extracting data...")
        mock_tqdm.write.assert_called_once_with("[INFO] Extracting data...")

    @patch('turbo_tosec.presenter.Console')
    def test_write_standard_delegates_to_console(self, mock_console):
        
        CLIPresenter.write_standard("Initialization complete.")
        mock_console.info.assert_called_once_with("Initialization complete.")