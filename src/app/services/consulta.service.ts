import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { EnvService } from './env.service';

@Injectable({
  providedIn: 'root',
})
export class ConsultaService {
  constructor(private http: HttpClient, private env: EnvService) {}

  findByCpf(cpf: string) {
    return [];
    // TODO: implementar
    // return this.http.get<any[]>(`${this.env.apiUrl}/consulta`).pipe(shareReplay());
  }

  findByNomeMaeData(nome: string, nomeMae: string, dataNascimento: string) {
    return [];
    // TODO: implementar
  }
}
