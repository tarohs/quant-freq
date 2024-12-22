量子化・サンプリング周波数デモプログラム
2024.12 by taroh (sasaki.taroh@gmail.com)

○ play版:

  * リアルタイムで周波数・ビット間引きした音を出力します

        usage: quant-freq-play.py FILENAME.wav [STARTSEC [ENDSEC]]

  * オプション:
    FILENAME.wav: wav形式のファイルを入力にとります
      - チャネル数は2 (ステレオ)、サンプリングビット数は16、また
        サンプリング周波数はデバイスで再生できるものを使って下さい
    STARTSEC, ENDSEC: 開始・終了の秒数指定

  * 操作: キー入力
   - 『1〜9abcdefg』: 1〜16 bit samplingにビット間引きします
   - 『!@#$%^&*』 (US keyboardのシフト『1〜8』): サンプリング間隔を
     1/1、1/2、……、1/128 に間引きます

  * PyAudio、wave、Numpy、SciPy あたりが必要です。
  * またPyAudioがPortAudioを必要とするため、先に入れて下さい
    (macOSならbrewから)。
  * PyAudioは、Python3.8 (動作確認しているのは3.8.13) では動いていたのに
    その後3.9で動かなくなりました。仕様だそうです。Condaなどで切り替えて
    3.8上で動作させて下さい
    - その後一瞬3.11では動いた気がするのですが……気のせいかも
    - 3.12以降? では、なにかデータ型のチェックでエラーになります
      (これはプログラムがまずい)。PyAudioが動く保証がないので
      直していません。
  * 周波数間引きは、単純間引き後にScyPyのLPF (scipy.signal.lfilter()) を
    かけていますが (かけないとじゃりじゃりしてわけがわからなくなるので)、
    当然のことながらカットオフ性能はこの関数によります。
    したがってカットオフ周波数の目安は表示していますが、スピーカから
    出力されている周波数はさらに制限されています
    (scipy.signal.lfilter() は-20dB/オクターブ らしい)
  * 出力デバイスはPyAudioのデフォルト出力デバイスです

○ plot版:

  * 周波数・ビット間引きした音をグラフ化します (元音の波形が黒・
    間引き後が赤)

        usage: quant-freq-plot.py FILENAME.wav StartSec EndSec \
                                  NBITS FREQ_NDIVBASE [lr]
            divide time 1, 2, 4, 8, ... when FREQ_NDIVBASE == 0, 1, 2, 3, ...
            plot L & R ch if lr option (otherwise plot L & L quantized)
        usage: quant-freq-play.py FILENAME.wav [STARTSEC [ENDSEC]]

  * オプション:
    FILENAME.wav: wav形式のファイルを入力にとります
      - チャネル数は2 (ステレオ)、サンプリングビット数は16
    StartSec, EndSec: 開始・終了の秒数指定
    NBITS: 量子化ビット数
    FREQ_NDIVBASE: 周波数を (1 / 2 ^(FREQ_NDIVBASE)) に間引きます
      (0、1、2、……に応じて1/1、1/2、1/4、……)
    lr: もしあればLまたはRチャネルを、なければ両チャネルの平均を
      元音として使用します

  * Numpy、matplotlib あたりが必要。
