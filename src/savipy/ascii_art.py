import argparse
import sys
from typing import Dict


ASCII_FONTS: Dict[str, Dict[str, str]] = {
    'standard': {
        'A': ' █████ \n██   ██\n███████\n██   ██\n██   ██',
        'B': '██████ \n██   ██\n██████ \n██   ██\n██████ ',
        'C': ' ██████\n██     \n██     \n██     \n ██████',
        'D': '██████ \n██   ██\n██   ██\n██   ██\n██████ ',
        'E': '███████\n██     \n█████  \n██     \n███████',
        'F': '███████\n██     \n█████  \n██     \n██     ',
        'G': ' ██████\n██     \n██   ██\n██   ██\n ██████',
        'H': '██   ██\n██   ██\n███████\n██   ██\n██   ██',
        'I': '██\n██\n██\n██\n██',
        'J': '     ██\n     ██\n     ██\n██   ██\n ██████',
        'K': '██   ██\n██  ██ \n█████  \n██  ██ \n██   ██',
        'L': '██     \n██     \n██     \n██     \n███████',
        'M': '███    ███\n████  ████\n██ ████ ██\n██  ██  ██\n██      ██',
        'N': '███    ██\n████   ██\n██ ██  ██\n██  ██ ██\n██   ████',
        'O': ' ██████ \n██    ██\n██    ██\n██    ██\n ██████ ',
        'P': '██████ \n██   ██\n██████ \n██     \n██     ',
        'Q': ' ██████ \n██    ██\n██ ██ ██\n██  ████\n ███████',
        'R': '██████ \n██   ██\n██████ \n██   ██\n██   ██',
        'S': ' ██████\n██     \n ██████\n      ██\n██████ ',
        'T': '████████\n   ██   \n   ██   \n   ██   \n   ██   ',
        'U': '██    ██\n██    ██\n██    ██\n██    ██\n ██████ ',
        'V': '██    ██\n██    ██\n██    ██\n ██  ██ \n  ████  ',
        'W': '██      ██\n██  ██  ██\n██ ████ ██\n████  ████\n███    ███',
        'X': '██   ██\n ██ ██ \n  ███  \n ██ ██ \n██   ██',
        'Y': '██   ██\n ██ ██ \n  ███  \n   ██  \n   ██  ',
        'Z': '███████\n    ██ \n   ██  \n  ██   \n███████',
        ' ': '   \n   \n   \n   \n   ',
        '!': '██\n██\n██\n  \n██',
        '?': ' ██████\n      ██\n  █████ \n        \n   ██   ',
        '.': '  \n  \n  \n  \n██',
        ',': '  \n  \n  \n██\n█ ',
        '0': ' ██████ \n██    ██\n██    ██\n██    ██\n ██████ ',
        '1': '   ██   \n ████   \n   ██   \n   ██   \n███████',
        '2': ' ██████ \n      ██\n ██████ \n██      \n███████',
        '3': ' ██████ \n      ██\n ██████ \n      ██\n ██████ ',
        '4': '██    ██\n██    ██\n███████ \n      ██\n      ██',
        '5': '███████ \n██      \n██████  \n      ██\n███████ ',
        '6': ' ██████ \n██      \n██████  \n██    ██\n ██████ ',
        '7': '███████\n     ██\n    ██ \n   ██  \n  ██   ',
        '8': ' ██████ \n██    ██\n ██████ \n██    ██\n ██████ ',
        '9': ' ██████ \n██    ██\n ███████\n      ██\n ██████ ',
    }
}


def text_to_ascii_art(text: str, font: str = 'standard') -> str:
    if font not in ASCII_FONTS:
        raise ValueError(f'Font "{font}" not available. Available fonts: {list(ASCII_FONTS.keys())}')

    font_dict = ASCII_FONTS[font]
    text = text.upper()

    lines = [''] * 5

    for char in text:
        if char in font_dict:
            char_lines = font_dict[char].split('\n')
            for i, line in enumerate(char_lines):
                lines[i] += line + '  '
        else:
            unknown_char = font_dict.get(' ', '   ')
            char_lines = unknown_char.split('\n')
            for i, line in enumerate(char_lines):
                lines[i] += line + '  '

    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate ASCII art from text',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ascii_art "HELLO"
  ascii_art "WORLD" --font standard
  echo "HELLO WORLD" | ascii_art
        '''
    )

    parser.add_argument(
        'text',
        nargs='?',
        help='Text to convert to ASCII art. If not provided, reads from stdin.'
    )

    parser.add_argument(
        '--font', '-f',
        default='standard',
        choices=list(ASCII_FONTS.keys()),
        help='Font to use for ASCII art (default: standard)'
    )

    parser.add_argument(
        '--list-fonts', '-l',
        action='store_true',
        help='List available fonts'
    )

    args = parser.parse_args()

    if args.list_fonts:
        print('Available fonts:')
        for font_name in ASCII_FONTS.keys():
            print(f'  {font_name}')
        return

    if args.text:
        text = args.text
    else:
        if sys.stdin.isatty():
            parser.error('No text provided. Either provide text as argument or pipe it via stdin.')
        text = sys.stdin.read().strip()

    if not text:
        parser.error('Empty text provided.')

    try:
        ascii_art = text_to_ascii_art(text, args.font)
        print(ascii_art)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()