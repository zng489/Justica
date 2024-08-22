import { Injectable, NgZone } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';
import { SnackMessengerComponent } from '@shared/components/snack-messenger/snack-messenger.component';
import { Message, MessageActions } from '@models/snack-message.model';

@Injectable({
  providedIn: 'root',
})
export class AvisoService {
  constructor(public snackBar: MatSnackBar, private zone: NgZone) {}

  private config(
    mensagem: string,
    tipo: string,
    icon: string,
    duration?: number
  ): MatSnackBarConfig {
    // Custom data utilizado no template do snack-messenget-component
    const customData = new Message();
    customData.text = mensagem;
    customData.action = MessageActions[tipo];
    customData.icon = `fas fa-${icon}`;

    // Configurações do snackbar
    const config = new MatSnackBarConfig();
    if (duration) {
      config.duration = duration; // em milissegundos
    }
    config.horizontalPosition = 'center';
    config.verticalPosition = 'top';
    config.panelClass = [`snack-bar-${tipo}-color`];
    config.data = { message: customData };

    return config;
  }

  putWarning(mensagem: string, { timeout = 3000 }: { timeout?: number } = {}) {
    this.zone.run(()=>
      this.snackBar.openFromComponent(
        SnackMessengerComponent,
        this.config(mensagem, 'warning', 'exclamation-circle', timeout)
      )
    );
  }

  putInfo(mensagem: string, { timeout = 3000 }: { timeout?: number } = {}) {
    this.zone.run(()=>
      this.snackBar.openFromComponent(
        SnackMessengerComponent,
        this.config(mensagem, 'info', 'info-circle', timeout)
      )
    );
  }

  putSuccess(mensagem: string, { timeout = 3000 }: { timeout?: number } = {}) {
    this.zone.run(()=>
      this.snackBar.openFromComponent(
        SnackMessengerComponent,
        this.config(mensagem, 'success', 'check-circle', timeout)
      )
    );
  }

  putError(mensagem: string, { timeout = 3000 }: { timeout?: number } = {}) {
    this.zone.run(()=>
      this.snackBar.openFromComponent(
        SnackMessengerComponent,
        this.config(mensagem, 'error', 'times-circle', timeout)
      )
    );
  }
}
