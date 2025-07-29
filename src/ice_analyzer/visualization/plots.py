import matplotlib.pyplot as plt
import numpy as np
import os

def visualize_test_files(files, window_size, custom_comments):
    """Erstellt Plots für alle Testdateien mit Metadaten und Zusatzinformationen."""
    # Plots vorbereiten
    fig, axes = plt.subplots(len(files), 1, figsize=(14, 5 * len(files)), sharex=True)

    # Wenn nur eine Datei, stelle sicher, dass axes iterierbar ist
    if len(files) == 1:
        axes = [axes]

    # Jede Datei einlesen und plotten
    for idx, file in enumerate(files):
        meta, time, force = read_data(file)
        meta, corrected_time = correct_start_time(meta)

        # Mittelwerte berechnen
        force_avg = moving_average(force, window_size)
        time_avg = time[:len(force_avg)]

        # Maxima berechnen
        max_idx = np.argmax(force)
        max_idx_avg = np.argmax(force_avg)

        # Plot erstellen
        ax = axes[idx]
        ax.plot(time, force, label="Rohdaten (F)", color="b", alpha=0.5)
        ax.plot(time_avg, force_avg, label=f"{window_size}-Punkt Mittelwert", color="g")
        ax.scatter(time[max_idx], force[max_idx], color='r', marker='+', s=100, label=f"Max: {force[max_idx]:.3f} N")
        ax.scatter(time_avg[max_idx_avg], force_avg[max_idx_avg], color='g', marker='+', s=100, label=f"Max Ø: {force_avg[max_idx_avg]:.3f} N")

        # Metadata Box
        ax.text(0.5, 0.95, "\n".join(meta),
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7),
                ha='left', va='top', transform=ax.transAxes, multialignment='left')

        # Suche passende Info-Datei
        info_file = os.path.join(os.path.dirname(file), "info_" + os.path.basename(file))
        if os.path.exists(info_file):
            with open(info_file, "r") as f:
                lines = f.readlines()
                info_lines = lines[:-8] if len(lines) > 8 else lines

                # Nur Ordner + Dateiname anzeigen
                short_path = os.path.join(os.path.basename(os.path.dirname(file)), os.path.basename(file))
                if info_lines:
                    info_lines[0] = f"Test File: {short_path}\n"

                info_text = "".join(info_lines)
        else:
            info_text = "Keine Info-Datei gefunden."

        # Info Box hinzufügen (unten rechts)
        ax.text(0.98, 0.05, info_text,
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7),
                ha='left', va='bottom', transform=ax.transAxes, multialignment='left')

        # Benutzerdefinierter Kommentar (oben rechts)
        filename_only = os.path.basename(file)
        user_comment = custom_comments.get(filename_only, "Kein Kommentar vorhanden.")
        ax.text(0.98, 0.75, user_comment,
                fontsize=10, bbox=dict(facecolor='white', alpha=0.7),
                ha='left', va='bottom', transform=ax.transAxes, multialignment='left')

        # Labels & Titel
        ax.legend()
        ax.set_ylabel("Kraft F (N)")
        ax.set_title(f"Kraft über Zeit - Datei {idx+1}: {os.path.basename(file)}")
        ax.grid()

    # Finalisieren
    plt.xlabel("Zeit (s)")
    plt.tight_layout()

    # Extrahiere Ordnername und Datum aus dem ersten Dateinamen
    parent_folder = os.path.basename(os.path.normpath(os.path.dirname(files[0])))

    # Extrahiere Datum aus dem ersten Dateinamen
    first_filename = os.path.basename(files[0])
    parts = first_filename.split("_")
    if len(parts) >= 4:
        try:
            date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
        except IndexError:
            date_str = "UnbekanntesDatum"
    else:
        date_str = "UnbekanntesDatum"

    # Speichern des Plots in hoher Auflösung
    output_filename = f"Biegefestigkeit_{parent_folder}_{date_str}.png"
    output_path = os.path.join(os.path.dirname(files[0]), output_filename)
    plt.savefig(output_path, dpi=300)  # Hohe Auflösung
    print(f"✅ Plot gespeichert als: {output_path}")
    plt.show()
    pass
