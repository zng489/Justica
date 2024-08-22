import { Component, OnInit, ChangeDetectionStrategy, ViewChild} from '@angular/core';
import { MatMenuTrigger } from '@angular/material/menu';
import { KeycloakService } from '@services/keycloak.service';
import { AvisoService } from '@services/aviso.service';
import { GraphService } from '@services/graph.service';
import { UserOptionsService } from '@services/user-options.service';

@Component({
  selector: 'userinfo',
  templateUrl: './userinfo.component.html',
  styleUrls: ['./userinfo.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserinfoComponent implements OnInit {
  user$ = this.securityService.userInfoData();
  @ViewChild(MatMenuTrigger) trigger: MatMenuTrigger;

  constructor(
    protected aviso: AvisoService,
    protected securityService: KeycloakService,
    private graph: GraphService,
    public userOptionService: UserOptionsService
  ) {}

  ngOnInit() {}

  public orderGraphRequest() {
    this.trigger.closeMenu();
    this.graph.orderGraph();
  }

  public infoGraphRequest() {
    this.trigger.closeMenu();
    this.graph.infoGraph();
  }

  public logout() {
    try {
      this.securityService.logout({ redirectUri: ''});
    } catch (error) {
      this.aviso.putError('Error ao realizar o logout!');
    }
  }
}
