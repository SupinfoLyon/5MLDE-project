import { Component } from '@angular/core';

@Component({
  selector: 'hero',
  templateUrl: './hero.component.html',
  styleUrls: ['./hero.component.scss']
})
export class HeroComponent {
  title = 'project-font';
  constructor() {}

  logger() {
    console.log('hero component');
  }
}
