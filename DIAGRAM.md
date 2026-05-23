classDiagram
    direction TB

    %% Presentation Layer
    namespace PresentationLayer {
        class CLIPresenter {
            +pbar: UniversalProgress
            +session: ImportSession
            +update_progress(current_bytes, total_bytes)
            +write_above_bar(msg)$
            +write_standard(msg)$
        }

        class UniversalProgress {
            +total: int
            +current: int
            +console_bar: tqdm
            +callback: Callable
            +update(n)
            +set_postfix(stats)
        }

        class Console {
            +info(msg)$
            +error(msg)$
            +warning(msg)$
        }
    }

    %% Core Engine Layer
    namespace CoreEngine {
        class ImportSession {
            +total_roms: int
            +error_count: int
            +db: DatabaseManager
            +parser: TurboParser
            +ingest(source, mode, callbacks...)
            -_run_direct_mode()
        }

        class TurboParser {
            +parse_to_arrow_stream(filepath) ArrowStream
        }

        class DatabaseManager {
            +conn: DuckDBConnection
            +setup_schema()
            +execute(query)
        }
    }

    %% Relationships
    CLIPresenter *-- UniversalProgress : Manages
    CLIPresenter o-- ImportSession : Reads Stats
    ImportSession *-- TurboParser : Uses
    ImportSession *-- DatabaseManager : Uses
    
    %% The Callback Bridge (Decoupling)
    CLIPresenter ..> ImportSession : Injects Callbacks