import { Component, OnInit, ChangeDetectionStrategy, ViewChild, AfterViewInit, Renderer2, Input, ChangeDetectorRef,  } from '@angular/core';
import { MatSlider } from '@angular/material/slider';
import { MatSlideToggle } from '@angular/material/slide-toggle';

@Component({
  selector: 'accessibility',
  templateUrl: './accessibility.component.html',
  styleUrls: ['./accessibility.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AccessibilityComponent implements OnInit, AfterViewInit {

  @Input() showIa = false;
  @Input() showShortcuts = true;

  @ViewChild(MatSlider, {static: false}) slider: MatSlider;
  @ViewChild(MatSlideToggle, {static: false}) toggleContrast: MatSlideToggle;

  constructor(private renderer: Renderer2, private cd: ChangeDetectorRef) { }

  ngOnInit() { 
   // Setting last theme option 
   if (localStorage.getItem('theme') === 'contrast') {
     document.body.classList.add('dark');
   }

   // Set last font-size option
   const fontSizeValue = localStorage.getItem('font-size');
   if (fontSizeValue) {
     document.body.style.fontSize = fontSizeValue;
   }
  }
  ngAfterViewInit(): void {
    // Setting toggle state to last theme selected if contrast
    if(document.body.classList.contains('dark')) {
      this.toggleContrast.checked = true;
    }

    // Setting silder to the last font-size value
    const fontSize = document.body.style.fontSize;
    if(fontSize && fontSize !== "1em") { 
      this.slider.value = parseFloat(fontSize.replace("em", ""));
    }

    this.slider.valueChange.subscribe(valor => {
      this.renderer.setStyle(document.body, 'font-size', valor + 'em');
      localStorage.setItem('font-size', valor + 'em' )
    });

    this.toggleContrast.toggleChange.subscribe(() => {

      if(!this.toggleContrast.checked) {
        this.renderer.setAttribute(document.querySelector('.logotipo .is-mobile'), 'src', '../../assets/images/uikit-logotipo-mobile-bw.svg');
        this.renderer.setAttribute(document.querySelector('.logotipo .is-desktop'), 'src', '../../assets/images/uikit-logotipo-bw.svg');
        this.renderer.addClass(document.body, 'dark');
        localStorage.setItem('theme', 'contrast')
      } else {
        this.renderer.setAttribute(document.querySelector('.logotipo .is-mobile'), 'src', '../../assets/images/uikit-logotipo-mobile.svg');
        this.renderer.setAttribute(document.querySelector('.logotipo .is-desktop'), 'src', '../../assets/images/uikit-logotipo.svg');
        this.renderer.removeClass(document.body, 'dark'); 
        localStorage.setItem('theme', 'light');
      }
    });

    // Avoiding error Expression has changed after it was checked
    this.cd.detectChanges();
  }
}
