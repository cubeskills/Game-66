import ai
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

def train_and_test(epoch):
    """Trainiert die KI und testet sie, gibt die Gewinnrate zurück."""
    ai_agent = ai.train_ai(epoch)
    print(f"\nTesten der KI nach {epoch} Trainings-Episoden:")
    wr = ai.test_ai(ai_agent, n_games=1000)
    return epoch, wr

if __name__ == "__main__":
    epochs = [2**i for i in range(22)]
    values = []

    # Parallelisiere die Arbeit mit ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        # Mappe die Funktion `train_and_test` auf die Liste `epochs`
        results = list(executor.map(train_and_test, epochs))

    # Sortiere die Ergebnisse nach den Epochen
    results.sort()
    epochs, values = zip(*results)

    # Plotten der Ergebnisse
    plt.plot(epochs, values, label="wr of ai against epoch")
    plt.xscale('log')  # Logarithmische Skala für die X-Achse
    plt.xlabel('Epochs')
    plt.ylabel('Win Rate (%)')
    plt.legend()
    plt.show()

