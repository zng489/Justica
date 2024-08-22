import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserOptionsService {

  private sisbajudOrdens: boolean = false;
  private infojud: boolean = false;

  constructor() { }

  setSisbajudOrdens(sisbajudOrdens: any) {
    this.sisbajudOrdens = sisbajudOrdens;
  }

  getSisbajudOrdens() {
    return this.sisbajudOrdens;
  }

  setInfojud(infojud: any) {
    this.infojud = infojud;
  }

  getInfojud() {
    return this.infojud;
  }
}
