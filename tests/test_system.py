import pytest
from unittest.mock import patch
from turbo_tosec.system import open_file_with_default_app, check_system_resources

class TestSystem:

    @patch('turbo_tosec.system.platform.system')
    @patch('turbo_tosec.system.os.startfile', create=True)
    def test_open_file_windows(self, mock_startfile, mock_platform):
        mock_platform.return_value = 'Windows'
        
        open_file_with_default_app("dummy.log")
        
        mock_startfile.assert_called_once_with("dummy.log")

    @patch('turbo_tosec.system.platform.system')
    @patch('turbo_tosec.system.subprocess.call')
    def test_open_file_mac(self, mock_call, mock_platform):
        mock_platform.return_value = 'Darwin'
        
        open_file_with_default_app("dummy.log")
        
        mock_call.assert_called_once_with(('open', "dummy.log"))

    @patch('turbo_tosec.system.platform.system')
    @patch('turbo_tosec.system.subprocess.call')
    def test_open_file_linux(self, mock_call, mock_platform):
        mock_platform.return_value = 'Linux'
        
        open_file_with_default_app("dummy.log")
        
        mock_call.assert_called_once_with(('xdg-open', "dummy.log"))

    @patch('builtins.print')
    @patch('turbo_tosec.system.platform.system')
    def test_open_file_handles_exceptions(self, mock_platform, mock_print):
        mock_platform.side_effect = Exception("Simulated OS Error")
        
        open_file_with_default_app("dummy.log")
        
        mock_print.assert_called_once()
        assert "Could not open log file automatically" in mock_print.call_args[0][0]

    @patch('builtins.print')
    @patch('turbo_tosec.system.os.cpu_count')
    def test_check_resources_optimal_configuration(self, mock_cpu, mock_print):
        mock_cpu.return_value = 8
        
        check_system_resources(workers=2, db_threads=2)
        
        mock_print.assert_any_call("System Resources: 8 CPU Cores detected.")
        mock_print.assert_any_call("Configuration looks good: 4 threads <= 8 cores.")

    @patch('builtins.print')
    @patch('turbo_tosec.system.os.cpu_count')
    def test_check_resources_bottleneck_warning(self, mock_cpu, mock_print):
        mock_cpu.return_value = 4
        
        check_system_resources(workers=4, db_threads=2)
        
        mock_print.assert_any_call("System Resources: 4 CPU Cores detected.")
        mock_print.assert_any_call("WARNING: You requested 8 concurrent threads (4 workers x 2 db_threads).")
        mock_print.assert_any_call("Your system only has 4 cores.")

    @patch('builtins.print')
    @patch('turbo_tosec.system.os.cpu_count')
    def test_check_resources_fallback_cpu_count(self, mock_cpu, mock_print):
        mock_cpu.return_value = None
        
        check_system_resources(workers=1, db_threads=1)
        
        mock_print.assert_any_call("System Resources: 1 CPU Cores detected.")

    @patch('builtins.print')
    @patch('turbo_tosec.system.os.cpu_count')
    def test_check_resources_handles_exceptions(self, mock_cpu, mock_print):
        mock_cpu.side_effect = Exception("Simulated CPU check failure")
        
        check_system_resources(workers=2, db_threads=2)
        
        mock_print.assert_called_once()
        assert "Resource check skipped:" in mock_print.call_args[0][0]
