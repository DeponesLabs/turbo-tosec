import pytest
from unittest.mock import patch
from turbo_tosec.crypto import calculate_file_hash, calculate_file_hash_gen

@pytest.fixture
def sample_file(tmp_path):

    file_path = tmp_path / "test_data.txt"
    file_path.write_bytes(b"test data")
    return str(file_path)

class TestCrypto:

    def test_calculate_file_hash_md5(self, sample_file):

        result = calculate_file_hash(sample_file, hash_algorithm="md5")
        assert result == "eb733a00c0c9d336e65691a37ab54293"

    def test_calculate_file_hash_sha1(self, sample_file):

        result = calculate_file_hash(sample_file, hash_algorithm="sha1")
        assert result == "f48dd853820860816c75d54d0f584dc863327a7c"

    def test_calculate_file_hash_unsupported_algorithm(self, sample_file):

        with pytest.raises(ValueError):
            calculate_file_hash(sample_file, hash_algorithm="sha256")

    @patch('builtins.print')
    def test_calculate_file_hash_exception_handling(self, mock_print, tmp_path):

        missing_file = str(tmp_path / "does_not_exist.txt")
        result = calculate_file_hash(missing_file, hash_algorithm="md5")
        
        mock_print.assert_called_once()
        assert result == "d41d8cd98f00b204e9800998ecf8427e"

    def test_calculate_file_hash_gen_yields_progress(self, sample_file):

        generator = calculate_file_hash_gen(sample_file, hash_algorithm="md5", chunk_size=4)
        progress_updates = []
        final_hash = None
        
        # In Python 3.3+, generators don't easily yield StopIteration when iterated over normally.
        # They may need to manually call next() to extract the returned value from StopIteration.
        while True:
            try:
                processed, total = next(generator)
                progress_updates.append((processed, total))
            except StopIteration as e:
                final_hash = e.value
                break
            
        assert len(progress_updates) == 3
        assert progress_updates[-1] == (9, 9)
        assert final_hash == "eb733a00c0c9d336e65691a37ab54293"

    def test_calculate_file_hash_gen_unsupported_algorithm(self, sample_file):
        
        with pytest.raises(ValueError):
            generator = calculate_file_hash_gen(sample_file, hash_algorithm="sha256")
            next(generator)