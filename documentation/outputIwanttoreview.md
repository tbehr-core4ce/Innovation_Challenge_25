synmara@Mac-2858 Innovation_Challenge_25 % pnpm 
Version 10.6.5 (compiled to binary; bundled Node.js v22.14.0)
Usage: pnpm [command] [flags]
       pnpm [ -h | --help | -v | --version ]

Manage your dependencies:
      add                  Installs a package and any packages that it depends on. By default, any new package is installed as a prod dependency
      import               Generates a pnpm-lock.yaml from an npm package-lock.json (or npm-shrinkwrap.json) file
   i, install              Install all dependencies for a project
  it, install-test         Runs a pnpm install followed immediately by a pnpm test
  ln, link                 Connect the local project to another one
      prune                Removes extraneous packages
  rb, rebuild              Rebuild a package
  rm, remove               Removes packages from node_modules and from the project's package.json
      unlink               Unlinks a package. Like yarn unlink but pnpm re-installs the dependency after removing the external link
  up, update               Updates packages to their latest version based on the specified range

Review your dependencies:
      audit                Checks for known security issues with the installed packages
      licenses             Check licenses in consumed packages
  ls, list                 Print all the versions of packages that are installed, as well as their dependencies, in a tree-structure
      outdated             Check for outdated packages

Run your scripts:
      exec                 Executes a shell command in scope of a project
      run                  Runs a defined package script
      start                Runs an arbitrary command specified in the package's "start" property of its "scripts" object
   t, test                 Runs a package's "test" script, if one was provided

Other:
      cat-file             Prints the contents of a file based on the hash value stored in the index file
      cat-index            Prints the index file of a specific package from the store
      find-hash            Experimental! Lists the packages that include the file with the specified hash.
      pack                 Create a tarball from a package
      publish              Publishes a package to the registry
      root                 Prints the effective modules directory

Manage your store:
      store add            Adds new packages to the pnpm store directly. Does not modify any projects or files outside the store
      store path           Prints the path to the active store directory
      store prune          Removes unreferenced (extraneous, orphan) packages from the store
      store status         Checks for modified packages in the store

Options:
  -r, --recursive          Run the command for each project in the workspace.
synmara@Mac-2858 Innovation_Challenge_25 % pnpm update
 ERR_PNPM_NO_PKG_MANIFEST  No package.json found in /Users/synmara/Documents/code/Innovation_Challenge_25
synmara@Mac-2858 Innovation_Challenge_25 % cd frontend 
synmara@Mac-2858 frontend % cd ..
synmara@Mac-2858 Innovation_Challenge_25 % cd backend 
synmara@Mac-2858 backend % python3 -m venv <betsvenv>
zsh: parse error near `\n'
synmara@Mac-2858 backend % python3 -m venv .betsvenv 
synmara@Mac-2858 backend % brew install pipx
==> Auto-updating Homebrew...
Adjust how often this is run with HOMEBREW_AUTO_UPDATE_SECS or disable with
HOMEBREW_NO_AUTO_UPDATE. Hide these hints with HOMEBREW_NO_ENV_HINTS (see `man brew`).
==> Downloading https://ghcr.io/v2/homebrew/portable-ruby/portable-ruby/blobs/sha256:20fa657858e44a4b39171d6e4111f8a9716eb62a78ebbd1491d94f90bb7b830a
################################################################################################################################################################ 100.0%
==> Pouring portable-ruby-3.4.5.arm64_big_sur.bottle.tar.gz
==> Homebrew collects anonymous analytics.
Read the analytics documentation (and how to opt-out) here:
  https://docs.brew.sh/Analytics
No analytics have been recorded yet (nor will be during this `brew` run).

==> Homebrew is run entirely by unpaid volunteers. Please consider donating:
  https://github.com/Homebrew/brew#donations

==> Auto-updated Homebrew!
Updated 2 taps (homebrew/core and homebrew/cask).
==> New Formulae
abpoa: SIMD-based C library for fast partial order alignment using adaptive band
act_runner: Action runner for Gitea based on Gitea's fork of act
addlicense: Scan directories recursively to ensure source files have license headers
aiac: Artificial Intelligence Infrastructure-as-Code Generator
aicommit2: Reactive CLI that generates commit messages for Git and Jujutsu with AI
aiken: Modern smart contract platform for Cardano
air: Fast and opinionated formatter for R code
airtable-mcp-server: MCP Server for Airtable
aklomp-base64: Fast Base64 stream encoder/decoder in C99, with SIMD acceleration
anchor: Solana Program Framework
anyzig: Universal zig executable that runs any version of zig
apache-polaris: Interoperable, open source catalog for Apache Iceberg
apigeecli: Apigee management API command-line interface
archgw: CLI for Arch Gateway
arp-scan-rs: ARP scan tool written in Rust for fast local network scans
asm-lsp: Language server for NASM/GAS/GO Assembly
assimp@5: Portable library for importing many well-known 3D model formats
atomic_queue: C++14 lock-free queues
attempt-cli: CLI for retrying fallible commands
audiowaveform: Generate waveform data and render waveform images from audio files
ayatana-ido: Ayatana Indicator Display Objects
b4: Tool to work with public-inbox and patch archives
backgroundremover: Remove background from images and video using AI
backlog-md: Markdown‑native Task Manager & Kanban visualizer for any Git repository
badread: Long read simulator that can imitate many types of read problems
bb-cli: Bitbucket Rest API CLI written in pure PHP
bedtk: Simple toolset for BED files
benchi: Benchmarking tool for data pipelines
blueprint-compiler: Markup language and compiler for GTK 4 user interfaces
bom: Utility to generate SPDX-compliant Bill of Materials manifests
brush: Bourne RUsty SHell (command interpreter)
bstring: Fork of Paul Hsieh's Better String Library
btcli: Bittensor command-line tool
btllib: Bioinformatics Technology Lab common code library
bulletty: Pretty feed reader (ATOM/RSS) that stores articles in Markdown files
bunster: Compile shell scripts to static binaries
burrow: Kafka Consumer Lag Checking
caesiumclt: Fast and efficient lossy and/or lossless image compression tool
cagent: Agent Builder and Runtime by Docker Engineering
cai: CLI tool for prompting LLMs
cargo-careful: Execute Rust code carefully, with extra checking along the way
cargo-clone: Cargo subcommand to fetch the source code of a Rust crate
cargo-component: Create WebAssembly components based on the component model proposal
cargo-geiger: Detects usage of unsafe Rust in a Rust crate and its dependencies
ccusage: CLI tool for analyzing Claude Code usage from local JSONL files
changelogen: Generate Beautiful Changelogs using Conventional Commits
chawan: TUI web browser with CSS, inline image and JavaScript support
chrome-devtools-mcp: Chrome DevTools for coding agents
clang-include-graph: Simple tool for visualizing and analyzing C/C++ project include graph
claude-cmd: Claude Code Commands Manager
claude-code-router: Tool to route Claude Code requests to different models and customize any request
claude-code-templates: CLI tool for configuring and monitoring Claude Code
claude-hooks: Hook system for Claude Code
claude-squad: Manage multiple AI agents like Claude Code, Aider and Codex in your terminal
claudekit: Intelligent guardrails and workflow automation for Claude Code
clipper2: Polygon clipping and offsetting library
clippy: Copy files from your terminal that actually paste into GUI apps
cliproxyapi: Wrap Gemini CLI, Codex, Claude Code, Qwen Code as an API service
codebook-lsp: Code-aware spell checker language server
cogapp: Small bits of Python computation for static files
config-file-validator: CLI tool to validate different configuration file types
container: Create and run Linux containers using lightweight virtual machines
container-canary: Test and validate container requirements against versioned manifests
container-compose: Manage Apple Container with Docker Compose files
context7-mcp: Up-to-date code documentation for LLMs and AI code editors
copyparty: Portable file server
corepack: Package acting as bridge between Node projects and their package managers
cpptrace: Simple, portable, and self-contained stacktrace library for C++11 and newer
credo: Static code analysis tool for the Elixir
ctrld: Highly configurable, multi-protocol DNS forwarding proxy
dagu: Lightweight and powerful workflow engine
damask-grid: Grid solver of DAMASK - Multi-physics crystal plasticity simulation package
darker: Apply Black formatting only in regions changed since last commit
dash-mpd-cli: Download media content from a DASH-MPEG or DASH-WebM MPD manifest
deck: Creates slide deck using Markdown and Google Slides
decker: HyperCard-like multimedia sketchpad
desed: Debugger for Sed
dexidp: OpenID Connect Identity and OAuth 2.0 Provider
diagram: CLI app to convert ASCII arts into hand drawn diagrams
dnglab: Camera RAW to DNG file format converter
dnote: Simple command-line notebook
docker-compose-langserver: Language service for Docker Compose documents
docker-debug: Use new container attach on already container go on debug
docmd: Minimal Markdown documentation generator
doge: Command-line DNS client
doh: Stand-alone DNS-over-HTTPS resolver using libcurl
domain-check: CLI tool for checking domain availability using RDAP and WHOIS protocols
doxx: Terminal document viewer for .docx files
dqlite: Embeddable, replicated and fault-tolerant SQLite-powered engine
dstp: Run common networking tests against your site
dumbpipe: Unix pipes between devices
dvisvgm: Fast DVI to SVG converter
eask-cli: CLI for building, running, testing, and managing your Emacs Lisp dependencies
eigen@3: C++ template library for linear algebra
electric: Real-time sync for Postgres
emmylua_ls: Lua Language Server
endlessh: SSH tarpit that slowly sends an endless banner
entt: Fast and reliable entity-component system for C++
erlang-language-platform: LSP server and CLI for the Erlang programming language
errcheck: Finds silently ignored errors in Go code
execstack: Utility to set/clear/query executable stack bit
faceprints: Detect and label images of faces using local Vision.framework models
fake-gcs-server: Emulator for Google Cloud Storage API
fakesteak: ASCII Matrix-like steak demo
fastmcp: Fast, Pythonic way to build MCP servers and clients
fennel-ls: Language Server for Fennel
fernflower: Advanced decompiler for Java bytecode
ffmate: FFmpeg automation layer
ffmpeg@7: Play, record, convert, and stream audio and video
filebrowser: Web File Browser
filen-cli: Interface with Filen, an end-to-end encrypted cloud storage service
fjira: Fuzzy-find cli jira interface
flexget: Multipurpose automation tool for content
forgejo: Self-hosted lightweight software forge
framework-tool-tui: TUI for controlling and monitoring Framework Computers hardware
fx-upscale: Metal-powered video upscaling
gbox: Provides environments for AI Agents to operate computer and mobile devices
gcl: GNU Common Lisp
gemini-cli: Interact with Google Gemini AI models from the command-line
gerust: Project generator for Rust backend projects
getparty: Multi-part HTTP download manager
ggc: Modern Git CLI
ghalint: GitHub Actions linter
ghidra: Multi-platform software reverse engineering framework
gitea-mcp-server: Interactive with Gitea instances with MCP
gitingest: Turn any Git repository into a prompt-friendly text ingest for LLMs
gitlab-ci-linter: Command-line tool to lint GitLab CI YAML files
gitlab-release-cli: Toolset to create, retrieve and update releases on GitLab
gitmux: Git status in tmux status bar
glom: Declarative object transformer and formatter, for conglomerating nested data
gnome-papers: Document viewer for PDF and other document formats aimed at the GNOME desktop
go-librespot: Spotify client
go-passbolt-cli: CLI for passbolt
go-rice: Easily embed resources like HTML, JS, CSS, images, and templates in Go
go@1.24: Open source programming language to build simple/reliable/efficient software
gocheat: TUI Cheatsheet for keybindings, hotkeys and more
goclone: Website Cloner
gonzo: Log analysis TUI
goodls: CLI tool to download shared files and folders from Google Drive
gpgmepp: C++ bindings for gpgme
gpgmepy: Python bindings for gpgme
gphotos-uploader-cli: Command-line tool to mass upload media folders to Google Photos
gradle@8: Open-source build automation tool based on the Groovy and Kotlin DSL
granted: Easiest way to access your cloud
gravitino: High-performance, geo-distributed, and federated metadata lake
gtrash: Featureful Trash CLI manager: alternative to rm and trash-cli
hack-browser-data: Command-line tool for decrypting and exporting browser data
haraka: Fast, highly extensible, and event driven SMTP server
harbor-cli: CLI for Harbor container registry
hdr10plus_tool: CLI utility to work with HDR10+ in HEVC files
hexhog: Hex viewer/editor
hierarchy-builder: High level commands to declare a hierarchy based on packed classes
htmlhint: Static code analysis tool you need for your HTML
httptap: HTTP request visualizer with phase-by-phase timing breakdown
ifopt: Light-weight C++ Interface to Nonlinear Programming Solvers
igrep: Interactive grep
imagineer: Image processing and conversion from the terminal
influxdb@2: Time series, events, and metrics database
intelli-shell: Like IntelliSense, but for shells
jiratui: Textual User Interface for interacting with Atlassian Jira from your shell
jq-lsp: Jq language server
jqp: TUI playground to experiment and play with jq
jwt-hack: JSON Web Token Hack Toolkit
kafkactl-aws-plugin: AWS Plugin for kafkactl
kafkactl-azure-plugin: Azure Plugin for kafkactl
kargo: Multi-Stage GitOps Continuous Promotion
kbt: Keyboard tester in terminal
kekkai: File integrity monitoring tool
kibi: Text editor in ≤1024 lines of code, written in Rust
kimi-cli: CLI agent for MoonshotAI Kimi platform
kingfisher: MongoDB's blazingly fast secret scanning and validation tool
kissat: Bare metal SAT solver
kokkos: C++ Performance Portability Ecosystem for parallel execution and abstraction
komac: Community Manifest Creator for Windows Package Manager (WinGet)
krane: Kubernetes deploy tool with rollout verification
ktea: Kafka TUI client
kubernetes-cli@1.33: Kubernetes command-line interface
kubernetes-mcp-server: MCP server for Kubernetes
lakekeeper: Apache Iceberg REST Catalog
lazycontainer: Terminal UI for Apple Containers
lazyssh: Terminal-based SSH manager
ldcli: CLI for managing LaunchDarkly feature flags
libayatana-appindicator: Ayatana Application Indicators Shared Library
libayatana-indicator: Ayatana Indicators Shared Library
libcaption: Free open-source CEA608 / CEA708 closed-caption encoder/decoder
libcpucycles: Microlibrary for counting CPU cycles
libdatrie: Double-Array Trie Library
libdbusmenu: GLib and Gtk Implementation of the DBusMenu protocol
libjodycode: Shared code used by several utilities written by Jody Bruchon
libngtcp2: IETF QUIC protocol implementation
libpq@17: Postgres C API library
libptytty: Library for OS-independent pseudo-TTY management
libselinux: SELinux library and simple utilities
libsepol: SELinux binary policy manipulation library
libudfread: Universal Disk Format reader
limine: Modern, advanced, portable, multiprotocol bootloader and boot manager
litehtml: Fast and lightweight HTML/CSS rendering engine
lld@20: LLVM Project Linker
llvm@20: Next-gen compiler infrastructure
lnk: Git-native dotfiles management that doesn't suck
lolcrab: Make your console colorful, with OpenSimplex noise
lsr: Ls but with io_uring
lstr: Fast, minimalist directory tree viewer
lue-reader: Terminal eBook reader with text-to-speech and multi-format support
lunarml: Standard ML compiler that produces Lua/JavaScript
lunasvg: SVG rendering and manipulation library in C++
lutgen: Blazingly fast interpolated LUT generator and applicator for color palettes
lzsa: Lossless packer that is optimized for fast decompression on 8-bit micros
mac-cleanup-py: Python cleanup script for macOS
magika: Fast and accurate AI powered file content types detection
manifold: Geometry library for topological robustness
mariadb@11.8: Drop-in replacement for MySQL
mark: Sync your markdown files with Confluence pages
mcat: Terminal image, video, directory, and Markdown viewer
mcp-atlassian: MCP server for Atlassian tools (Confluence, Jira)
mcp-get: CLI for discovering, installing, and managing MCP servers
mcp-google-sheets: MCP server integrates with your Google Drive and Google Sheets
mcp-grafana: MCP server for Grafana
mcp-inspector: Visual testing tool for MCP servers
mcp-proxy: Bridge between Streamable HTTP and stdio MCP transports
mcp-publisher: Publisher CLI tool for the Official Model Context Protocol (MCP) Registry
mcp-server-chart: MCP with 25+ @antvis charts for visualization, generation, and analysis
mcp-server-kubernetes: MCP Server for kubernetes management commands
mcphost: CLI host for LLMs to interact with tools via MCP
mcptools: CLI for interacting with MCP servers using both stdio and HTTP transport
mdserve: Fast markdown preview server with live reload and theme support
media-control: Control and observe media playback from the command-line
melt: Backup and restore Ed25519 SSH keys with seed words
memtier_benchmark: Redis and Memcache traffic generation and benchmarking tool
mermaid-cli: CLI for Mermaid library
min-lang: Small but practical concatenative programming language and shell
minify: Minifier for HTML, CSS, JS, JSON, SVG, and XML
mk: Wrapper for auto-detecting build and test commands in a repository
mklittlefs: Creates LittleFS images for ESP8266, ESP32, Pico RP2040, and RP2350
mlc: Check for broken links in markup files
mlx-lm: Run LLMs with MLX
mongo-c-driver@1: C driver for MongoDB
moodle-dl: Downloads course content fast from Moodle (e.g., lecture PDFs)
moribito: TUI for LDAP Viewing/Queries
mpremote: Tool for interacting remotely with MicroPython devices
msedit: Simple text editor with clickable interface
msolve: Library for Polynomial System Solving through Algebraic Methods
mysql-to-sqlite3: Transfer data from MySQL to SQLite
n8n-mcp: MCP for Claude Desktop, Claude Code, Windsurf, Cursor to build n8n workflows
nanoarrow: Helpers for Arrow C Data & Arrow C Stream interfaces
nanobot: Build MCP Agents
nessie: Transactional Catalog for Data Lakes with Git-like semantics
netscanner: Network scanner with features like WiFi scanning, packetdump and more
nextflow: Reproducible scientific workflows
ni: Selects the right Node package manager based on lockfiles
nifi-toolkit: Command-line utilities to setup and support NiFi
nixfmt: Command-line tool to format Nix language code
node@24: Open-source, cross-platform JavaScript runtime environment
notion-mcp-server: MCP Server for Notion
npq: Audit npm packages before you install them
nuxi: Nuxt CLI (nuxi) for creating and managing Nuxt projects
nx: Smart, Fast and Extensible Build System
nyan: Colorizing `cat` command with syntax highlighting
oasis: CLI for interacting with the Oasis Protocol network
oatpp: Light and powerful C++ web framework
omekasy: Converts alphanumeric input to various Unicode styles
omnara: Talk to Your AI Agents from Anywhere
onigmo: Regular expressions library forked from Oniguruma
openapi: CLI tools for working with OpenAPI, Arazzo and Overlay specifications
openapv: Open Advanced Professional Video Codec
openblas64: Optimized BLAS library
opencode: AI coding agent, built for the terminal
openlist: New AList fork addressing anti-trust issues
openssl@3.5: Cryptography and SSL/TLS Toolkit
osx-trash: Allows trashing of files instead of tempting fate with rm
oterm: Terminal client for Ollama
ovsx: Command-line interface for Eclipse Open VSX
pelican: Static site generator that supports Markdown and reST syntax
permify: Open-source authorization service & policy engine based on Google Zanzibar
pg-schema-diff: Diff Postgres schemas and generating SQL migrations
pgslice: Postgres partitioning as easy as pie
pgstream: PostgreSQL replication with DDL changes
php-intl: PHP internationalization extension
plakar: Create backups with compression, encryption and deduplication
playwright-mcp: MCP server for Playwright
plutobook: Paged HTML Rendering Library
plutoprint: Generate PDFs and Images from HTML
plutovg: Tiny 2D vector graphics library in C
podcast-archiver: Archive all episodes from your favorite podcasts
portable-libffi: Portable Foreign Function Interface library
portable-libxcrypt: Extended crypt library for descrypt, md5crypt, bcrypt, and others
portable-libyaml: YAML Parser
portable-openssl: Cryptography and SSL/TLS Toolkit
portable-ruby: Powerful, clean, object-oriented scripting language
portable-zlib: General-purpose lossless data-compression library
postgres-language-server: Language Server for Postgres
postgresql@18: Object-relational database system
precice: Coupling library for partitioned multi-physics simulations
privatebin-cli: CLI for creating and managing PrivateBin pastes
protozero: Minimalist protocol buffer decoder and encoder in C++
pulp-cli: Command-line interface for Pulp 3
pulumictl: Swiss army knife for Pulumi development
pyrefly: Fast type checker and IDE for Python
pyscn: Intelligent Python Code Quality Analyzer
python-gdbm@3.14: Python interface to gdbm
python-tk@3.14: Python interface to Tcl/Tk
python@3.14: Interpreted, interactive, object-oriented programming language
pytr: Use TradeRepublic in terminal and mass download all documents
q: Tiny command-line DNS client with support for UDP, TCP, DoT, DoH, DoQ and ODoH
qcoro6: C++ Coroutines for Qt
qman: Modern man page viewer
qrkey: Generate and recover QR codes from files for offline private key backup
qt3d: Provides functionality for near-realtime simulation systems
qt5compat: Qt 5 Core APIs that were removed in Qt 6
qtbase: Cross-platform application and UI framework
qtcharts: UI Components for displaying visually pleasing charts
qtconnectivity: Provides access to Bluetooth hardware
qtdatavis3d: Provides functionality for 3D visualization
qtdeclarative: QML, Qt Quick and several related modules
qtgraphs: Provides functionality for 2D and 3D graphs
qtgrpc: Provides support for communicating with gRPC services
qthttpserver: Framework for embedding an HTTP server into a Qt application
qtimageformats: Plugins for additional image formats: TIFF, MNG, TGA, WBMP
qtlanguageserver: Implementation of the Language Server Protocol and JSON-RPC
qtlocation: Provides C++ interfaces to retrieve location and navigational information
qtlottie: Display graphics and animations exported by the Bodymovin plugin
qtmultimedia: Provides APIs for playing back and recording audiovisual content
qtnetworkauth: Provides support for OAuth-based authorization to online services
qtpositioning: Provides access to position, satellite info and area monitoring classes
qtquick3d: Provides a high-level API for creating 3D content or UIs based on Qt Quick
qtquick3dphysics: High-level QML module adding physical simulation capabilities to Qt Quick 3D
qtquickeffectmaker: Tool to create custom Qt Quick shader effects
qtquicktimeline: Enables keyframe-based animations and parameterization
qtremoteobjects: Provides APIs for inter-process communication
qtscxml: Provides functionality to create state machines from SCXML files
qtsensors: Provides access to sensors via QML and C++ interfaces
qtserialbus: Provides access to serial industrial bus interfaces
qtserialport: Provides classes to interact with hardware and virtual serial ports
qtshadertools: Provides tools for the cross-platform Qt shader pipeline
qtspeech: Enables access to text-to-speech engines
qtsvg: Classes for displaying the contents of SVG files
qttools: Facilitate the design, development, testing and deployment of applications
qttranslations: Qt translation catalogs
qtvirtualkeyboard: Provides an input framework and reference keyboard frontend
qtwayland: Wayland platform plugin and QtWaylandCompositor API
qtwebchannel: Bridges the gap between Qt applications and HTML/JavaScript
qtwebengine: Provides functionality for rendering regions of dynamic web content
qtwebsockets: Provides WebSocket communication compliant with RFC 6455
qtwebview: Displays web content in a QML application
quadcastrgb: Set RGB lights on HyperX QuadCast S and Duocast microphones
quint: Core tool for the Quint specification language
qwen-code: AI-powered command-line workflow tool for developers
radvd: IPv6 Router Advertisement Daemon
rails-mcp-server: MCP server for Rails applications
recur: Retry a command with exponential backoff and jitter
reddix: Reddit, refined for the terminal
rggen: Code generation tool for control and status registers
rmpc: Terminal based Media Player Client with album art support
rnp: High performance C++ OpenPGP library used by Mozilla Thunderbird
rocq-elpi: Elpi extension language for Rocq
rolesanywhere-credential-helper: Manages getting temporary security credentials from IAM Roles Anywhere
rqbit: Fast command-line bittorrent client and server
rsql: CLI for relational databases and common data file formats
rulesync: Unified AI rules management CLI tool
rv: Ruby version manager
salesforce-mcp: MCP Server for interacting with Salesforce instances
samply: CLI sampling profiler
sarif-tools: Set of command-line tools and Python library for working with SARIF files
scdl: Command-line tool to download music from SoundCloud
secretspec: Declarative secrets management tool
seqan3: Modern C++ library for sequence analysis
sherif: Opinionated, zero-config linter for JavaScript monorepos
shimmy: Small local inference server with OpenAI-compatible GGUF endpoints
shortest: AI-powered natural language end-to-end testing framework
slack-mcp-server: Powerful MCP Slack Server with multiple transports and smart history fetch logic
snooze: Run a command at a particular time
somo: Human-friendly alternative to netstat for socket and port monitoring
sox_ng: Sound eXchange NG
specify: Toolkit to help you get started with Spec-Driven Development
spice-server: Implements the server side of the SPICE protocol
sprocket: Bioinformatics workflow engine built on the Workflow Description Language (WDL)
sqlite-rsync: SQLite remote copy tool
sqlite3-to-mysql: Transfer data from SQLite to MySQL
sqruff: Fast SQL formatter/linter
standardebooks: Tools for producing ebook files
stormy: Minimal, customizable and neofetch-like weather CLI based on rainy
stringtie: Transcript assembly and quantification for RNA-Seq
stu: TUI explorer application for Amazon S3 (AWS S3)
supabase: Open source Firebase alternative
supabase-mcp-server: MCP Server for Supabase
swag: Automatically generate RESTful API documentation with Swagger 2.0 for Go
swift-section: CLI tool for parsing mach-o files to obtain Swift information
tabixpp: C++ wrapper to tabix indexer
taskline: Tasks, boards & notes for the command-line habitat
taze: Modern cli tool that keeps your deps fresh
tdd-guard: Automated TDD enforcement for Claude Code
teamtype: Peer-to-peer, editor-agnostic collaborative editing of local text files
termsvg: Record, share and export your terminal as a animated SVG image
terraform-mcp-server: MCP server for Terraform
terratag: CLI to automate tagging for AWS, Azure & GCP resources in Terraform
teslamate: Self-hosted data logger for your Tesla
tfmcp: Terraform Model Context Protocol (MCP) Tool
tfplugingen-openapi: OpenAPI to Terraform Provider Code Generation Specification
tfstate-lookup: Lookup resource attributes in tfstate
tiledb: Universal storage engine
tiny-remapper: Tiny, efficient tool for remapping JAR files using "Tiny"-format mappings
tkrzw: Set of implementations of DBM
tofu-ls: OpenTofu Language Server
tombi: TOML formatter, linter and language server
toml-bombadil: Dotfile manager with templating
tracetest: Build integration and end-to-end tests
tree-sitter-cli: Parser generator tool
tscriptify: Golang struct to TypeScript class/interface converter
tsnet-serve: Expose HTTP applications to a Tailscale Tailnet network
tuios: Terminal UI OS (Terminal Multiplexer)
tun2proxy: Tunnel (TUN) interface for SOCKS and HTTP proxies
tweakcc: Customize your Claude Code themes, thinking verbs, and more
two-ms: Detect secrets in files and communication platforms
typtea: Minimal terminal-based typing speed tester
unitycatalog: Open, Multi-modal Catalog for Data & AI
urx: Extracts URLs from OSINT Archives for Security Insights
uvwasi: WASI syscall API built atop libuv
varlock: Add declarative schema to .env files using @env-spec decorator comments
vgo: Project scaffolder for Go, written in Go
vibe-log-cli: CLI tool for analyzing Claude Code sessions
videoalchemy: Toolkit expanding video processing capabilities
vineflower: Java decompiler
volcano-cli: CLI for Volcano, Cloud Native Batch System
vsd: Download video streams over HTTP, DASH (.mpd), and HLS (.m3u8)
vtcode: CLI Semantic Coding Agent
wait4x: Wait for a port or a service to enter the requested state
wal-g: Archival restoration tool for databases
wassette: Security-oriented runtime that runs WebAssembly Components via MCP
wayback: Archiving tool integrated with various archival services
wgpu-native: Native WebGPU implementation based on wgpu-core
wishlist: Single entrypoint for multiple SSH endpoints
wuppiefuzz: Coverage-guided REST API fuzzer developed on top of LibAFL
wxwidgets@3.2: Cross-platform C++ GUI toolkit
yaml2json: Command-line tool convert from YAML to JSON
yamlresume: Resumes as code in YAML
yek: Fast Rust based tool to serialize text-based files for LLM consumption
yuque-dl: Knowledge base downloader for Yuque
zig@0.14: Programming language designed for robustness, optimality, and clarity
zsv: Tabular data swiss-army knife CLI
zuban: Python language server and type checker, written in Rust

You have 18 outdated formulae installed.

==> Fetching downloads for: pipx
==> Downloading https://ghcr.io/v2/homebrew/core/pipx/manifests/1.8.0-1
################################################################################################################################################################ 100.0%
==> Fetching dependencies for pipx: mpdecimal, ca-certificates, openssl@3, readline, sqlite, xz, lz4, zstd and python@3.14
==> Downloading https://ghcr.io/v2/homebrew/core/mpdecimal/manifests/4.0.1
################################################################################################################################################################ 100.0%
==> Fetching mpdecimal
==> Downloading https://ghcr.io/v2/homebrew/core/mpdecimal/blobs/sha256:e21da583e42e86d5a2f0aedfaf7820e51b8af3065da599cff179d1a39903f3ab
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/ca-certificates/manifests/2025-11-04-1
################################################################################################################################################################ 100.0%
==> Fetching ca-certificates
==> Downloading https://ghcr.io/v2/homebrew/core/ca-certificates/blobs/sha256:c414336ff5220d77124debb496c8d86ffa1bbc5946309ee2d9d26645db300b96
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/openssl/3/manifests/3.6.0
################################################################################################################################################################ 100.0%
==> Fetching openssl@3
==> Downloading https://ghcr.io/v2/homebrew/core/openssl/3/blobs/sha256:9a8fa2ae1ef3424b116d7e6422d979e0290f4affdef072b1592e4535d2617d92
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/readline/manifests/8.3.1
################################################################################################################################################################ 100.0%
==> Fetching readline
==> Downloading https://ghcr.io/v2/homebrew/core/readline/blobs/sha256:3afa0c228ce704810d09d40ce7d1265777df8b9034a7bfc18f0f4c19094710a8
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/sqlite/manifests/3.51.0
################################################################################################################################################################ 100.0%
==> Fetching sqlite
==> Downloading https://ghcr.io/v2/homebrew/core/sqlite/blobs/sha256:8a986b66c97e295a5a9908b531528535dd30f23c42bde5cfcbdd258f097d868a
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/xz/manifests/5.8.1
################################################################################################################################################################ 100.0%
==> Fetching xz
==> Downloading https://ghcr.io/v2/homebrew/core/xz/blobs/sha256:dcd7823f2624cbcd08f55c232097a79300c7d76ab5969004db1a4785c6c0cd87
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/lz4/manifests/1.10.0-1
################################################################################################################################################################ 100.0%
==> Fetching lz4
==> Downloading https://ghcr.io/v2/homebrew/core/lz4/blobs/sha256:5bd143b7b784989e549637ea4e484af85ba481e640dde69bc35f3843ae25abc6
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/zstd/manifests/1.5.7-1
################################################################################################################################################################ 100.0%
==> Fetching zstd
==> Downloading https://ghcr.io/v2/homebrew/core/zstd/blobs/sha256:55a4e0a4a92f5cf4885295214914de4aefad2389884085185e9ce87b4edae946
################################################################################################################################################################ 100.0%
==> Downloading https://ghcr.io/v2/homebrew/core/python/3.14/manifests/3.14.0_1
################################################################################################################################################################ 100.0%
==> Fetching python@3.14
==> Downloading https://ghcr.io/v2/homebrew/core/python/3.14/blobs/sha256:f59474e8481341bf8308aaa1ca7cd553a8db19c7aab64f6402fba55fe2c6fc1a
################################################################################################################################################################ 100.0%
==> Fetching pipx
==> Downloading https://ghcr.io/v2/homebrew/core/pipx/blobs/sha256:3fef69289fa10429ad0ec47931aa8433dc19dbe5ba3a8ae1048ddf4716c4df22
################################################################################################################################################################ 100.0%
==> Installing dependencies for pipx: mpdecimal, ca-certificates, openssl@3, readline, sqlite, xz, lz4, zstd and python@3.14
==> Installing pipx dependency: mpdecimal
==> Downloading https://ghcr.io/v2/homebrew/core/mpdecimal/manifests/4.0.1
Already downloaded: /Users/synmara/Library/Caches/Homebrew/downloads/dbbf60721dc54b6215f6c0988496331d4110a2a358da867a1129cd84b8166b31--mpdecimal-4.0.1.bottle_manifest.json
==> Pouring mpdecimal--4.0.1.arm64_sequoia.bottle.tar.gz
🍺  /opt/homebrew/Cellar/mpdecimal/4.0.1: 22 files, 645.7KB
==> Installing pipx dependency: ca-certificates
==> Downloading https://ghcr.io/v2/homebrew/core/ca-certificates/manifests/2025-11-04-1
Already downloaded: /Users/synmara/Library/Caches/Homebrew/downloads/c8e8f0b8441bc94be20cccded08d1ed3f0f8faccadc00c3ae6f3e5bb20c6e98c--ca-certificates-2025-11-04-1.bottle_manifest.json
==> Pouring ca-certificates--2025-11-04.all.bottle.1.tar.gz
==> Regenerating CA certificate bundle from keychain, this may take a while...
🍺  /opt/homebrew/Cellar/ca-certificates/2025-11-04: 4 files, 235.8KB
==> Installing pipx dependency: openssl@3
==> Downloading https://ghcr.io/v2/homebrew/core/openssl/3/manifests/3.6.0
Already downloaded: /Users/synmara/Library/Caches/Homebrew/downloads/403c903e557d19d801f4c6b4f635c9553af72a487024139a5773e636c884ef9e--openssl@3-3.6.0.bottle_manifest.json
==> Pouring openssl@3--3.6.0.arm64_sequoia.bottle.tar.gz
