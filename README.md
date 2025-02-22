# Trading Bot Fyers

This repository contains a trading bot for Fyers.

## Getting Started

### Prerequisites

- Python 3.13
- Git

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/trading-bot-fyers.git
    cd trading-bot-fyers
    ```

2. Run the installation script based on your operating system:

    For Windows:
    ```sh
    install.bat
    ```

    For Unix-based systems:
    ```sh
    ./install.sh
    ```

3. Add your API information in the [.env](http://_vscodecontentref_/1) file. You can find this file in the root directory of the project. Update it with your Fyers API credentials.

### Running the FastAPI Server

Once you have completed the above steps, you can start the FastAPI server by running:

```sh
python app/main.py
```

The server should now be running, and you can access it at `http://localhost:5000`.

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.